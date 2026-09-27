import pytest

from harness.config import HarnessConfig


def test_config_defaults_to_claude(monkeypatch):
    monkeypatch.delenv("MODEL_PROVIDER", raising=False)
    monkeypatch.setenv("FOUNDRY_ENDPOINT", "https://example.services.ai.azure.com")
    monkeypatch.setenv("CLAUDE_DEPLOYMENT", "claude")

    config = HarnessConfig.from_env()

    assert config.provider == "claude"
    assert config.deployment_for("claude") == "claude"


def test_config_rejects_unknown_provider(monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "other")

    with pytest.raises(ValueError, match="MODEL_PROVIDER"):
        HarnessConfig.from_env()

    config = HarnessConfig("claude", "", None, None, None)
    with pytest.raises(ValueError, match="provider"):
        config.deployment_for("other")


def test_config_requires_selected_deployment():
    config = HarnessConfig("claude", "", None, None, None)

    with pytest.raises(ValueError, match="deployment"):
        config.deployment_for("claude")
