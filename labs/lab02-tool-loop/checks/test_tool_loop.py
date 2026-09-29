import pytest

from harness.ledger import Usage
from harness.models import ScriptedModel, ToolCall, Turn
from harness.tool_loop import run_tool_loop


def test_tool_loop_returns_tool_result_to_next_turn():
    model = ScriptedModel([
        Turn(text="", tool_calls=[ToolCall("call_1", "echo", {"text": "hello"})], stop="tool",
             usage=Usage(input_tokens=3, output_tokens=1)),
        Turn(text="done", usage=Usage(input_tokens=5, output_tokens=2)),
    ])

    result = run_tool_loop(model, "task", "system", {"echo": lambda args: args["text"]})

    assert result.text == "done"
    assert result.usage == Usage(input_tokens=8, output_tokens=3)


def test_tool_loop_returns_unknown_tool_error():
    class RecordingModel(ScriptedModel):
        def __init__(self):
            super().__init__([
                Turn(text="", tool_calls=[ToolCall("call_1", "missing", {})], stop="tool"),
                Turn(text="done"),
            ])
            self.calls = []

        def complete(self, **kwargs):
            self.calls.append(kwargs)
            return super().complete(**kwargs)

    model = RecordingModel()
    assert run_tool_loop(model, "task", "system", {}).text == "done"
    assert model.calls[1]["messages"][-1]["content"][0]["output"] == "ERROR: unknown tool missing"


def test_tool_loop_stops_at_iteration_cap():
    model = ScriptedModel([
        Turn(text="", tool_calls=[ToolCall(str(index), "echo", {})], stop="tool")
        for index in range(3)
    ])

    with pytest.raises(RuntimeError, match="max_iterations"):
        run_tool_loop(model, "task", "system", {"echo": lambda _: "ok"}, max_iterations=2)


def test_tool_loop_records_run_statistics():
    from harness.tool_loop import LoopStats

    model = ScriptedModel([
        Turn(text="", tool_calls=[
            ToolCall("call_1", "echo", {"text": "hello"}),
            ToolCall("call_2", "missing", {}),
        ], stop="tool"),
        Turn(text="done"),
    ])
    stats = LoopStats()
    announced = []

    result = run_tool_loop(
        model, "task", "system", {"echo": lambda args: args["text"]},
        on_model_call=announced.append, stats=stats,
    )

    assert result.text == "done"
    assert announced == [1, 2]
    assert (stats.model_calls, stats.tool_calls, stats.tool_errors) == (2, 2, 1)
    assert stats.model_seconds >= 0 and stats.tool_seconds >= 0
