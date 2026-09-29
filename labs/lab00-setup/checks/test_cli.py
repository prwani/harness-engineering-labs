import json
from types import SimpleNamespace

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


def test_ask_prints_answer_and_usage(monkeypatch):
    from harness.cli import learner
    from harness.models import ScriptedModel, Turn

    monkeypatch.setattr(learner, "create_model_client", lambda: ScriptedModel([Turn(
        text="391", usage=SimpleNamespace(input_tokens=4, output_tokens=1)
    )]))

    result = runner.invoke(app, ["ask", "What is 17 times 23?"])

    assert result.exit_code == 0
    assert "391" in result.output
    assert "input=4, output=1" in result.output


def test_ask_without_question_reuses_prompt_after_each_response(monkeypatch):
    from harness.cli import learner
    from harness.models import ScriptedModel, Turn

    questions = iter(["What is 2 + 2?", "What is 3 + 3?", "/exit"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(questions))
    monkeypatch.setattr(
        learner, "create_model_client",
        lambda: ScriptedModel([Turn(text="4"), Turn(text="6")]),
    )

    result = runner.invoke(app, ["ask"])

    assert result.exit_code == 0
    assert "Interactive harness" in result.output
    assert result.output.count("Assistant>") == 2
    assert "4" in result.output
    assert "6" in result.output
