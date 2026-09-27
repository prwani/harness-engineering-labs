from harness.models import ScriptedModel, ToolCall, Turn
from harness.tool_loop import run_tool_loop


def test_tool_loop_is_retained():
    model = ScriptedModel([Turn(text="", tool_calls=[ToolCall("1", "echo", {})]), Turn(text="done")])
    assert run_tool_loop(model, "task", "system", {"echo": lambda _: "ok"}).text == "done"
