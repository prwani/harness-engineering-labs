from harness.bare import run_bare
from harness.models import ScriptedModel, Turn


def test_bare_call_is_stateless_and_tool_free():
    turn = run_bare(
        ScriptedModel([Turn(text="report")]),
        task="Produce a report",
        system="Return a report.",
    )

    assert turn.text == "report"
    assert turn.tool_calls == []
