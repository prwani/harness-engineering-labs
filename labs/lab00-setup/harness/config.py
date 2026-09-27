"""Non-secret configuration and Entra credential creation."""

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class HarnessConfig:
    provider: str
    endpoint: str
    claude_deployment: str | None
    gpt_deployment: str | None
    project_endpoint: str | None

    @classmethod
    def from_env(cls) -> "HarnessConfig":
        provider = os.getenv("MODEL_PROVIDER", "claude")
        if provider not in {"claude", "gpt"}:
            raise ValueError("MODEL_PROVIDER must be 'claude' or 'gpt'")
        return cls(
            provider=provider,
            endpoint=os.getenv("FOUNDRY_ENDPOINT", ""),
            claude_deployment=os.getenv("CLAUDE_DEPLOYMENT"),
            gpt_deployment=os.getenv("GPT_DEPLOYMENT"),
            project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
        )

    def deployment_for(self, provider: str) -> str:
        deployment = self.claude_deployment if provider == "claude" else self.gpt_deployment
        if not deployment:
            raise ValueError(f"{provider.upper()} deployment is not configured")
        return deployment


def foundry_token_provider():
    """Return the SDK-compatible Entra bearer-token provider."""
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    return get_bearer_token_provider(
        DefaultAzureCredential(), "https://ai.azure.com/.default"
    )
