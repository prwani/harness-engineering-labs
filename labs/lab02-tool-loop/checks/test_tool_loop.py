from harness.models import ScriptedModel, ToolCall, Turn
from harness.tool_loop import run_tool_loop


def test_tool_loop_returns_tool_result_to_next_turn():
    model = ScriptedModel([
        Turn(text="", tool_calls=[ToolCall("call_1", "echo", {"text": "hello"})], stop="tool"),
        Turn(text="done"),
    ])

    result = run_tool_loop(model, "task", "system", {"echo": lambda args: args["text"]})

    assert result.text == "done"
