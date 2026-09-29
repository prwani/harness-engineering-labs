import json

import pytest
from typer.testing import CliRunner

from harness.cli.app import app


runner = CliRunner()


def test_ping_probes_and_preserves_capabilities(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("FOUNDRY_ENDPOINT", "https://example.services.ai.azure.com")
    monkeypatch.setenv("GPT_DEPLOYMENT", "gpt")

    result = runner.invoke(app, ["ping", "--provider", "gpt", "--probe"])

    assert result.exit_code == 0
    assert json.loads((tmp_path / "runs/capabilities.json").read_text())["gpt"]["deployment"] == "gpt"


def test_ping_rejects_missing_endpoint(monkeypatch):
    monkeypatch.delenv("FOUNDRY_ENDPOINT", raising=False)

    result = runner.invoke(app, ["ping"])

    assert result.exit_code != 0
    assert "FOUNDRY_ENDPOINT" in result.output


def test_ask_uses_tool_loop(monkeypatch, tmp_path):
    from harness.cli import learner
    from harness.models import ScriptedModel, Turn

    monkeypatch.setattr(learner, "create_model_client", lambda: ScriptedModel([Turn(text="answer")]))

    result = runner.invoke(app, ["ask", "--repo", str(tmp_path), "What is in this repository?"])

    assert result.exit_code == 0
    assert "answer" in result.output
    assert "Tokens:" in result.output


def test_ask_without_question_keeps_repository_prompt_available(monkeypatch, tmp_path):
    from harness.cli import learner
    from harness.models import ScriptedModel, Turn

    questions = iter(["What is in this repository?", "Show the latest commit.", "/exit"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(questions))
    monkeypatch.setattr(
        learner, "create_model_client",
        lambda: ScriptedModel([Turn(text="Files found."), Turn(text="Commit found.")]),
    )

    result = runner.invoke(app, ["ask", "--repo", str(tmp_path)])

    assert result.exit_code == 0
    assert result.output.count("Assistant>") == 2
    assert "Files found." in result.output
    assert "Commit found." in result.output


def test_ask_reports_hook_denial_without_running_shell(monkeypatch, tmp_path):
    from harness.cli import learner
    from harness.models import ScriptedModel, ToolCall, Turn

    monkeypatch.setattr(
        learner, "create_model_client",
        lambda: ScriptedModel([
            Turn(text="", tool_calls=[ToolCall("blocked", "shell", {"command": "echo demo"})]),
            Turn(text="The hook denied shell execution."),
        ]),
    )
    monkeypatch.setattr(
        "harness.tools._run_shell",
        lambda *args, **kwargs: pytest.fail("shell command executed"),
    )

    result = runner.invoke(app, ["ask", "--repo", str(tmp_path), "Run shell"])

    assert result.exit_code == 0
    assert "Hook: denied shell: shell commands are disabled in Lab 2B" in result.output
    assert "The hook denied shell execution." in result.output
