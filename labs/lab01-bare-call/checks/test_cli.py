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


def test_ask_prints_bare_answer_and_usage(monkeypatch):
    from harness.cli import learner
    from harness.models import ScriptedModel, Turn

    monkeypatch.setattr(learner, "create_model_client", lambda: ScriptedModel([Turn(
        text="Tokyo", usage=SimpleNamespace(input_tokens=5, output_tokens=2)
    )]))

    result = runner.invoke(app, ["ask", "What is the capital of Japan?"])

    assert result.exit_code == 0
    assert "Tokyo" in result.output
    assert "input=5, output=2" in result.output
