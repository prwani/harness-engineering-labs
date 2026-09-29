import pytest

from harness.learner import ask_with_tools
from harness.models import ScriptedModel, ToolCall, Turn
from harness.tools import build_tools


def test_repository_helpers_are_rooted_and_cli_tools_are_registered(tmp_path):
    (tmp_path / "README.md").write_text("hello")
    tools, definitions = build_tools(tmp_path)

    assert tools["list_files"]({"path": "."}) == "README.md"
    assert {tool["name"] for tool in definitions} == set(tools)
    assert {"git_cli", "azure_cli", "shell"} <= set(tools)
    with pytest.raises(ValueError, match="outside"):
        tools["read_file"]({"path": "../outside.txt"})


def test_cli_tools_forward_unrestricted_arguments(monkeypatch, tmp_path):
    calls = []

    def fake_run(command, *, cwd, timeout=15):
        calls.append((command, cwd, timeout))
        return "ok"

    monkeypatch.setattr("harness.tools._run", fake_run)
    tools, _ = build_tools(tmp_path)

    assert tools["git_cli"]({"args": ["reset", "--hard", "HEAD"]}) == "ok"
    assert tools["azure_cli"]({"args": ["group", "delete", "--name", "demo", "--yes"]}) == "ok"
    assert calls == [
        (["git", "reset", "--hard", "HEAD"], tmp_path.resolve(), 30),
        (["az", "group", "delete", "--name", "demo", "--yes"], tmp_path.resolve(), 60),
    ]


def test_shell_runs_command_without_allow_list(monkeypatch, tmp_path):
    calls = []

    def fake_run_shell(command, *, cwd, timeout=30):
        calls.append((command, cwd, timeout))
        return "ok"

    monkeypatch.setattr("harness.tools._run_shell", fake_run_shell)
    tools, _ = build_tools(tmp_path)

    assert tools["shell"]({"command": "echo unrestricted && whoami"}) == "ok"
    assert calls == [("echo unrestricted && whoami", tmp_path.resolve(), 30)]


def test_learner_question_runs_read_tool_and_returns_answer(tmp_path):
    (tmp_path / "README.md").write_text("A sample project")
    client = ScriptedModel([
        Turn(text="", tool_calls=[ToolCall("call_1", "read_file", {"path": "README.md"})]),
        Turn(text="The README describes a sample project."),
    ])

    result = ask_with_tools(client, "Summarize README.md", repo=tmp_path)

    assert result.text == "The README describes a sample project."
