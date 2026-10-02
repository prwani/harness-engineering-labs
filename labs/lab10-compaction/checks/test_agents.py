import subprocess
import sys
import time

import pytest
from typer.testing import CliRunner

from harness import background
from harness.cli import learner
from harness.cli.app import app
from harness.agents import discover_agents, parse_agent
from harness.models import ToolCall, Turn

runner = CliRunner()


class Recorder:
    def __init__(self, *turns):
        self.turns = iter(turns)
        self.calls = []

    def complete(self, *, system, messages, tools, **_):
        self.calls.append({"system": system, "tools": [tool["name"] for tool in tools],
                           "messages": list(messages)})
        return next(self.turns)


def make_agent(repo, name="reviewer", tools="list_files, read_file"):
    path = repo / ".harness" / "agents" / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\nname: {name}\ndescription: Reviews code.\ntools: {tools}\n---\n\nYou review code.\n")
    return path


def test_agent_definitions(tmp_path):
    agent = parse_agent(make_agent(tmp_path, tools="read_file, mcp__orders__*"), "project")
    assert agent.allows("read_file") and agent.allows("mcp__orders__list_orders")
    assert not agent.allows("write_file")
    assert list(discover_agents(tmp_path)) == ["reviewer"]
    with pytest.raises(ValueError, match="cannot run other agents"):
        parse_agent(make_agent(tmp_path, "nested", "read_file, run_agent"), "project")


def test_subagent_has_its_own_context_tools_and_transcript(tmp_path, monkeypatch):
    make_agent(tmp_path)
    (tmp_path / "app.py").write_text("SECRET = 1\n")
    model = Recorder(
        Turn(text="", tool_calls=[ToolCall("a", "run_agent", {"agent": "reviewer", "task": "Review app.py"})]),
        Turn(text="", tool_calls=[ToolCall("r", "read_file", {"path": "app.py"}),
                                  ToolCall("w", "write_file", {"path": "x.py", "content": ""})]),
        Turn(text="One finding: a secret in app.py:1."),
        Turn(text="Summary: one finding."),
    )
    monkeypatch.setattr(learner, "create_model_client", lambda: model)

    result = runner.invoke(app, ["ask", "--repo", str(tmp_path), "Review the code"])

    assert result.exit_code == 0, result.output
    parent, child = model.calls[0], model.calls[1]
    assert "run_agent" in parent["tools"] and "reviewer: Reviews code." in parent["system"]
    assert child["tools"] == ["list_files", "read_file"]
    assert child["system"].startswith("You review code.")
    assert [m["role"] for m in child["messages"]] == ["user"]
    assert "Tool: reviewer:read_file" in result.output
    assert "reviewer:write_file" in result.output and not (tmp_path / "x.py").exists()
    summary = model.calls[3]["messages"][-1]["content"][0]["output"]
    assert summary.startswith("Agent reviewer finished (2 LLM calls, 2 tool calls, 1 denied")
    assert "SECRET = 1" not in str(model.calls[3]["messages"])
    transcripts = list(tmp_path.parent.glob("**/*.agents/01-reviewer.jsonl"))
    assert transcripts and "SECRET = 1" in transcripts[0].read_text()


def git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q", "-b", "main")
    git(tmp_path, "config", "user.email", "t@example.com")
    git(tmp_path, "config", "user.name", "T")
    (tmp_path / "a.txt").write_text("a\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-q", "-m", "init")
    return tmp_path


def wait_done(repo, name):
    for _ in range(100):
        if background.load(repo, name).exit_code is not None:
            return background.load(repo, name)
        time.sleep(0.1)
    raise AssertionError("background agent did not finish")


def test_background_agent_runs_in_its_own_worktree(repo):
    script = "from pathlib import Path; Path('COVERAGE.md').write_text('ok'); print('wrote it')"
    agent = background.start(repo, "coverage", "measure", command=[sys.executable, "-c", script])

    done = wait_done(repo, "coverage")
    assert done.status == "done"
    worktree = repo / ".harness" / "worktrees" / "coverage"
    assert (worktree / "COVERAGE.md").read_text() == "ok"
    assert not (repo / "COVERAGE.md").exists()
    assert "worktree-coverage" in subprocess.run(["git", "branch"], cwd=repo, capture_output=True, text=True).stdout
    assert "wrote it" in runner.invoke(app, ["logs", "coverage", "--repo", str(repo)]).output
    assert "coverage" in runner.invoke(app, ["agents", "--repo", str(repo)]).output
    with pytest.raises(ValueError, match="exists"):
        background.start(repo, "coverage", "again", command=[sys.executable, "-c", ""])

    refused = runner.invoke(app, ["rm", "coverage", "--repo", str(repo)])
    assert refused.exit_code == 1 and "uncommitted changes" in refused.output
    (worktree / "COVERAGE.md").unlink()
    assert runner.invoke(app, ["rm", "coverage", "--repo", str(repo)]).exit_code == 0
    assert not worktree.exists()
    assert background.list_agents(repo) == [] and agent.name == "coverage"


def test_bg_option_needs_a_name(tmp_path):
    result = runner.invoke(app, ["ask", "--repo", str(tmp_path), "--bg", "task"])
    assert result.exit_code == 1 and "--bg needs -n NAME" in result.output
