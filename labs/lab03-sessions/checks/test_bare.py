from harness.bare import run_bare
from harness.models import ScriptedModel, Turn


def test_bare_call_is_retained():
    assert run_bare(ScriptedModel([Turn(text="report")]), "task", "system").text == "report"
