import pytest

from harness.graph import Graph, GraphState, RouteConfirmationRequired, UnknownNodeError


def test_conditional_routing_picks_branch_from_state():
    graph = Graph()
    graph.add_node("classify", lambda state: state.with_data(kind="delete"))
    graph.add_node("delete_branch", lambda state: state.with_data(handled="delete"))
    graph.add_node("update_branch", lambda state: state.with_data(handled="update"))
    graph.add_route("classify", lambda state: "delete_branch" if state.data["kind"] == "delete" else "update_branch")
    graph.add_route("delete_branch", lambda _state: "END")

    result = graph.run("classify", GraphState())

    assert result.data["handled"] == "delete"
    assert result.visited == ("classify", "delete_branch")


def test_unknown_node_raises():
    graph = Graph()
    graph.add_node("start", lambda state: state)
    graph.add_route("start", lambda _state: "missing")

    with pytest.raises(UnknownNodeError):
        graph.run("start", GraphState())


def test_idempotent_nodes_do_not_reexecute_with_same_key():
    calls = []

    def node(state):
        calls.append(1)
        return state.with_data(count=state.data.get("count", 0) + 1)

    graph = Graph()
    graph.add_node("increment", node)
    graph.add_route("increment", lambda _state: "END")

    state = GraphState()
    state = state.mark_executed("increment")  # simulate a resumed run
    result = graph.run("increment", state, idempotency_key=lambda name, _state: name)

    assert calls == []
    assert result.data.get("count", 0) == 0


def test_human_route_confirmation_blocks_without_confirmation():
    graph = Graph()
    graph.add_node("plan", lambda state: state)
    graph.add_node("write", lambda state: state.with_data(written=True))
    graph.add_route("plan", lambda _state: "write", requires_confirmation=True)
    graph.add_route("write", lambda _state: "END")

    with pytest.raises(RouteConfirmationRequired):
        graph.run("plan", GraphState())


def test_human_route_confirmation_proceeds_once_confirmed():
    graph = Graph()
    graph.add_node("plan", lambda state: state)
    graph.add_node("write", lambda state: state.with_data(written=True))
    graph.add_route("plan", lambda _state: "write", requires_confirmation=True)
    graph.add_route("write", lambda _state: "END")

    result = graph.run("plan", GraphState(), confirmations={"plan"})

    assert result.data["written"] is True
