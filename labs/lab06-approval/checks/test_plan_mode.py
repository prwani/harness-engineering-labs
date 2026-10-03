from typer.testing import CliRunner

from harness.cli import learner
from harness.cli.app import app
from harness.learner import ask_with_tools
from harness.models import ToolCall, Turn
from harness.plan_mode import plan_mode_policy, render_todos
from harness.todos import TodoList

runner = CliRunner()


class Recorder:
    """Scripted model that records the tools and system prompt of every call."""

    def __init__(self, turns):
        self.turns = iter(turns)
        self.calls = []

    def complete(self, *, system, messages, tools, **_):
        self.calls.append({"system": system, "tools": [tool["name"] for tool in tools],
                           "last": messages[-1]})
        return next(self.turns)


def test_plan_policy_allows_reads_and_denies_changes():
    assert plan_mode_policy("read_file", {"path": "a.py"}).allowed
    assert plan_mode_policy("git_cli", {"args": ["diff", "--stat"]}).allowed
    assert plan_mode_policy("git_cli", {"args": ["branch", "-a"]}).allowed
    assert not plan_mode_policy("write_file", {"path": "a.py", "content": ""}).allowed
    assert not plan_mode_policy("git_cli", {"args": ["commit", "-m", "x"]}).allowed
    assert not plan_mode_policy("git_cli", {"args": ["branch", "feature/x"]}).allowed


def test_plan_mode_hides_write_tools_and_denies_a_write(tmp_path):
    model = Recorder([
        Turn(text="", tool_calls=[ToolCall("w", "write_file", {"path": "x.py", "content": "1"})]),
        Turn(text="Plan: ..."),
    ])
    denials = []

    ask_with_tools(model, "Plan it", repo=tmp_path, mode="plan", todos=TodoList(),
                   on_hook_denial=lambda name, reason: denials.append(reason))

    assert "write_file" not in model.calls[0]["tools"]
    assert "edit_file" not in model.calls[0]["tools"]
    assert "write_todos" in model.calls[0]["tools"]
    assert "PLAN MODE" in model.calls[0]["system"]
    assert denials and "plan mode" in denials[0]
    assert not (tmp_path / "x.py").exists()


def test_write_todos_updates_harness_state_and_reminds_the_model(tmp_path):
    todos, changes = TodoList(), []
    model = Recorder([
        Turn(text="", tool_calls=[ToolCall("t", "write_todos", {"todos": [
            {"text": "add discounts.csv"}, {"text": "add tests", "done": True}]})]),
        Turn(text="Planned."),
        Turn(text="Working."),
    ])

    ask_with_tools(model, "Plan", repo=tmp_path, mode="plan", todos=todos, on_todos=changes.append)
    ask_with_tools(model, "Go", repo=tmp_path, todos=todos)

    assert render_todos(todos) == "[ ] add discounts.csv\n[x] add tests"
    assert changes == [todos]
    assert "Open todos:\n- add discounts.csv" in model.calls[2]["system"]
    assert "write_file" in model.calls[2]["tools"]


def test_cli_plan_then_execute_and_todos_survive_continue(tmp_path, monkeypatch):
    model = Recorder([
        Turn(text="", tool_calls=[ToolCall("t", "write_todos", {"todos": [{"text": "step one"}]})]),
        Turn(text="Here is the plan."),
        Turn(text="Implemented."),
    ])
    monkeypatch.setattr(learner, "create_model_client", lambda: model)

    result = runner.invoke(app, ["ask", "--repo", str(tmp_path), "--plan"],
                           input="Plan discount codes\n/todos\n/execute Use a dataclass.\n/exit\n")

    assert result.exit_code == 0, result.output
    assert "Plan mode: write tools are off" in result.output
    assert "[ ] step one" in result.output
    assert "write_file" not in model.calls[0]["tools"]
    assert "write_file" in model.calls[2]["tools"]
    assert model.calls[2]["last"]["content"].startswith("The plan is approved.")
    assert model.calls[2]["last"]["content"].endswith("Use a dataclass.")

    resumed = runner.invoke(app, ["ask", "--repo", str(tmp_path), "-c"], input="/todos\n/exit\n")
    assert "[ ] step one" in resumed.output
