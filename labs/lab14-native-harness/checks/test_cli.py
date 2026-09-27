import json

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
