"""Typed graph state, conditional routing, idempotent nodes and human route
confirmation.

A graph is a set of named nodes over a typed state object. Each node is a
pure function ``state -> state`` keyed by an idempotency key so re-running
an edge after a crash never double-applies effects. Routing between nodes
is a conditional function of state, and some routes require a human to
confirm before the graph proceeds (e.g. crossing into a write-heavy branch).
"""

from dataclasses import dataclass, field, replace
from typing import Any, Callable


class UnknownNodeError(Exception):
    pass


class RouteConfirmationRequired(Exception):
    """Raised when a route requires human confirmation that hasn't been given."""

    def __init__(self, route: str) -> None:
        super().__init__(f"route requires human confirmation: {route}")
        self.route = route


@dataclass(frozen=True)
class GraphState:
    """A minimal typed state envelope. Extend via ``data`` for lab-specific
    fields while keeping ``visited`` and ``executed_keys`` harness-owned."""

    data: dict[str, Any] = field(default_factory=dict)
    visited: tuple[str, ...] = ()
    executed_keys: frozenset[str] = frozenset()

    def with_data(self, **updates: Any) -> "GraphState":
        return replace(self, data={**self.data, **updates})

    def mark_visited(self, node: str) -> "GraphState":
        return replace(self, visited=self.visited + (node,))

    def mark_executed(self, key: str) -> "GraphState":
        return replace(self, executed_keys=self.executed_keys | {key})

    def already_executed(self, key: str) -> bool:
        return key in self.executed_keys


NodeFn = Callable[[GraphState], GraphState]
RouteFn = Callable[[GraphState], str]


@dataclass
class Graph:
    nodes: dict[str, NodeFn] = field(default_factory=dict)
    routes: dict[str, RouteFn] = field(default_factory=dict)
    confirm_required: set[str] = field(default_factory=set)

    def add_node(self, name: str, fn: NodeFn) -> None:
        self.nodes[name] = fn

    def add_route(self, name: str, route: RouteFn, *, requires_confirmation: bool = False) -> None:
        self.routes[name] = route
        if requires_confirmation:
            self.confirm_required.add(name)

    def run(
        self,
        start: str,
        state: GraphState,
        confirmations: set[str] | None = None,
        idempotency_key: Callable[[str, GraphState], str] | None = None,
    ) -> GraphState:
        confirmations = confirmations or set()
        node_name = start
        while node_name != "END":
            if node_name not in self.nodes:
                raise UnknownNodeError(node_name)
            key = idempotency_key(node_name, state) if idempotency_key else node_name
            if not state.already_executed(key):
                state = self.nodes[node_name](state)
                state = state.mark_executed(key)
            state = state.mark_visited(node_name)
            route = self.routes.get(node_name)
            if route is None:
                break
            if node_name in self.confirm_required and node_name not in confirmations:
                raise RouteConfirmationRequired(node_name)
            node_name = route(state)
        return state
