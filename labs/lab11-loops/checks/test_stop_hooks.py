import json

from typer.testing import CliRunner

from harness.cli import learner
from harness.cli.app import app
from harness.hooks import HookPipeline, load_project_hooks
from harness.models import ToolCall, Turn
from harness.tool_loop import LoopStats, run_tool_loop

runner = CliRunner()


class Recorder:
    def __init__(self, *turns):
        self.turns = iter(turns)
        self.calls = []

    def complete(self, *, system, messages, tools, **_):
        self.calls.append(list(messages))
        return next(self.turns)


def test_stop_hook_sends_the_model_back_until_satisfied():
    answers = iter(["tests fail", "still failing", None])
    seen = []

    def gate(text, active):
        seen.append((text, active))
        return next(answers)

    model = Recorder(Turn(text="done?"), Turn(text="done now?"), Turn(text="really done"))
    stats = LoopStats()
    turn = run_tool_loop(model, "fix it", "system", {}, max_iterations=5, stats=stats,
                         hooks=HookPipeline(stop=(gate,)))

    assert turn.text == "really done" and stats.stop_blocks == 2 and stats.model_calls == 3
    assert seen == [("done?", False), ("done now?", True), ("really done", True)]
    last = model.calls[-1]
    assert last[-1]["role"] == "user" and "attempt 2/3" in last[-1]["content"]
    assert "still failing" in last[-1]["content"]


def test_the_loop_bounds_a_stop_hook_that_never_agrees():
    model = Recorder(*[Turn(text=f"answer {n}") for n in range(5)])
    stats = LoopStats()
    turn = run_tool_loop(model, "fix it", "system", {}, max_iterations=10, stats=stats,
                         hooks=HookPipeline(stop=(lambda text, active: "no",)))
    assert turn.text == "answer 3" and stats.stop_blocks == 3


def write_settings(repo, script):
    hooks = repo / ".harness" / "hooks"
    hooks.mkdir(parents=True)
    (hooks / "gate.py").write_text(script)
    (repo / ".harness" / "settings.json").write_text(json.dumps(
        {"hooks": {"stop": [{"command": ["python", ".harness/hooks/gate.py"]}]}}))


def test_stop_command_hooks_get_the_event_on_stdin(tmp_path):
    write_settings(tmp_path, "import json, sys\nevent = json.load(sys.stdin)\n"
                             "if 'DONE' in event['last_message']: sys.exit(0)\n"
                             "print('active=%s' % event['stop_hook_active'], file=sys.stderr)\nsys.exit(2)\n")
    feedback = []
    hooks = load_project_hooks(tmp_path, lambda name, message: feedback.append((name, message)))

    assert hooks.on_stop("DONE", False) is None
    assert hooks.on_stop("not yet", True) == "Stop hook feedback (.harness/hooks/gate.py):\nactive=True"
    assert feedback == [("stop", "active=True")]


def test_cli_shows_stop_hook_feedback_and_bounds_iterations(tmp_path, monkeypatch):
    monkeypatch.setenv("HARNESS_HOME", str(tmp_path / "home"))
    write_settings(tmp_path, "import sys\nprint('tests are red', file=sys.stderr)\nsys.exit(2)\n")
    model = Recorder(Turn(text="done"), Turn(text="done again"))
    monkeypatch.setattr(learner, "create_model_client", lambda: model)

    result = runner.invoke(app, ["ask", "--repo", str(tmp_path), "--max-iterations", "2", "fix"])

    assert result.exit_code == 1
    assert "Hook: stop: tests are red" in result.output
    assert "max_iterations" in result.output and len(model.calls) == 2


def test_plan_mode_skips_stop_hooks(tmp_path, monkeypatch):
    monkeypatch.setenv("HARNESS_HOME", str(tmp_path / "home"))
    write_settings(tmp_path, "import sys\nsys.exit(2)\n")
    model = Recorder(Turn(text="the plan"))
    monkeypatch.setattr(learner, "create_model_client", lambda: model)
    result = runner.invoke(app, ["ask", "--repo", str(tmp_path), "--plan", "plan it"])
    assert result.exit_code == 0 and "stop_blocks" not in result.output
