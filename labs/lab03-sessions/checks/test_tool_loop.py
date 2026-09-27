from harness.models import ScriptedModel, ToolCall, Turn
from harness.tool_loop import run_tool_loop


def test_tool_loop_returns_tool_result_to_next_turn():
    model = ScriptedModel([
        Turn(text="", tool_calls=[ToolCall("call_1", "echo", {"text": "hello"})], stop="tool"),
        Turn(text="done"),
    ])

    result = run_tool_loop(model, "task", "system", {"echo": lambda args: args["text"]})

    assert result.text == "done"


def test_tool_loop_returns_unknown_tool_error():
    model = ScriptedModel([
        Turn(text="", tool_calls=[ToolCall("call_1", "missing", {})], stop="tool"),
        Turn(text="done"),
    ])

    assert run_tool_loop(model, "task", "system", {}).text == "done"


def test_tool_loop_stops_at_iteration_cap():
    model = ScriptedModel([
        Turn(text="", tool_calls=[ToolCall(str(index), "echo", {})], stop="tool")
        for index in range(3)
    ])

    try:
        run_tool_loop(model, "task", "system", {"echo": lambda _: "ok"}, max_iterations=2)
    except RuntimeError as error:
        assert "max_iterations" in str(error)
    else:
        raise AssertionError("expected an iteration-cap error")
