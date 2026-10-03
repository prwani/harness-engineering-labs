import json

from typer.testing import CliRunner

from harness.cli import learner
from harness.cli.app import app
from harness.models import ToolCall, Turn
from harness.pge import parse_verdict, run_pge

runner = CliRunner()


class Recorder:
    def __init__(self, *turns):
        self.turns = iter(turns)
        self.calls = []

    def complete(self, *, system, messages, tools, **_):
        self.calls.append({"system": system, "tools": [tool["name"] for tool in tools],
                           "messages": list(messages)})
        return next(self.turns)


PASS = Turn(text='{"verdict": "PASS", "failed_criteria": [], "feedback": "All met."}')
FAIL = Turn(text='{"verdict": "FAIL", "failed_criteria": ["2. tax is rounded"], "feedback": "Tax is off by one cent."}')


def test_parse_verdict_fails_safe():
    assert parse_verdict(PASS.text).verdict == "PASS"
    assert parse_verdict("```json\n" + FAIL.text + "\n```").failed_criteria == ["2. tax is rounded"]
    assert parse_verdict("Looks good to me!").verdict == "FAIL"
    assert parse_verdict('{"verdict": "MAYBE"}').verdict == "FAIL"


def test_roles_have_separate_tools_and_a_fresh_evaluator(tmp_path):
    model = Recorder(
        Turn(text="", tool_calls=[ToolCall("w", "write_file", {"path": "x.py", "content": "x"})]),
        Turn(text="# Plan\n1. receipt command"),
        Turn(text="", tool_calls=[ToolCall("g", "write_file", {"path": "receipt.py", "content": "R = 1\n"})]),
        Turn(text="Implemented."),
        FAIL,
        Turn(text="Fixed the tax."),
        PASS,
    )
    plans = []
    result = run_pge(model, "Add a receipt command", tmp_path, runs_dir=tmp_path / ".runs",
                     approve_plan=lambda plan: plans.append(plan.read_text()) or True)

    planner, generator, evaluator, revision = (model.calls[0], model.calls[2], model.calls[4],
                                               model.calls[5])
    assert planner["tools"] == ["list_files", "read_file", "git_status", "git_log"]
    assert not (tmp_path / "x.py").exists() and result.nodes[0].denied == 1
    assert plans == ["# Plan\n1. receipt command\n"]
    assert generator["tools"] == ["list_files", "read_file", "write_file", "edit_file", "run_tests"]
    assert (tmp_path / "receipt.py").read_text() == "R = 1\n"
    assert evaluator["tools"] == ["list_files", "read_file", "run_tests", "git_status", "git_cli"]
    assert len(evaluator["messages"]) == 1 and "Implemented." not in json.dumps(evaluator["messages"])
    assert "Tax is off by one cent." in revision["messages"][0]["content"]
    assert result.outcome == "PASS" and [v.verdict for v in result.verdicts] == ["FAIL", "PASS"]
    assert [run.name for run in result.nodes] == ["planner", "generator-0", "evaluator-0",
                                                  "generator-1", "evaluator-1"]
    events = [json.loads(line) for line in result.trace.read_text().splitlines()]
    assert [e["verdict"] for e in events if e["event"] == "verdict"] == ["FAIL", "PASS"]
    assert events[-1]["event"] == "run_end" and events[-1]["outcome"] == "PASS"


def test_revisions_are_bounded_and_the_gate_can_stop(tmp_path):
    model = Recorder(Turn(text="plan"), Turn(text="done"), FAIL, Turn(text="done"), FAIL)
    result = run_pge(model, "feature", tmp_path, approve_plan=lambda plan: True, max_revisions=1)
    assert result.outcome == "FAIL" and len(result.verdicts) == 2

    model = Recorder(Turn(text="plan"))
    result = run_pge(model, "feature", tmp_path, approve_plan=lambda plan: False)
    assert result.outcome == "STOPPED" and len(model.calls) == 1


def test_cli_gate_and_ablation(tmp_path, monkeypatch):
    monkeypatch.setenv("HARNESS_HOME", str(tmp_path / "home"))
    model = Recorder(Turn(text="# Plan"), Turn(text="Implemented."))
    monkeypatch.setattr(learner, "create_model_client", lambda: model)

    result = runner.invoke(app, ["pge", "--repo", str(tmp_path), "--no-evaluator", "Add receipt"],
                           input="y\n")

    assert result.exit_code == 0, result.output
    assert "PLAN.md written. Review it now" in result.output
    assert "[planner] started" in result.output and "[generator-0] llm_calls=1" in result.output
    assert "Generated without an evaluator" in result.output and "trace=" in result.output
    assert len(model.calls) == 2

    model = Recorder(Turn(text="# Plan"))
    monkeypatch.setattr(learner, "create_model_client", lambda: model)
    result = runner.invoke(app, ["pge", "--repo", str(tmp_path), "Add receipt"], input="n\n")
    assert result.exit_code == 0 and "Plan not approved" in result.output
