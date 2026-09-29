"""Create a Foundry-backed model client using the current Entra identity."""

from harness.config import HarnessConfig, foundry_token_provider
from harness.models.adapters import MessagesAdapter, ModelClient, ResponsesAdapter


def create_model_client() -> ModelClient:
    from dotenv import load_dotenv

    load_dotenv()
    config = HarnessConfig.from_env()
    if not config.endpoint:
        raise ValueError("FOUNDRY_ENDPOINT is not configured; copy .env.example to .env")

    deployment = config.deployment_for(config.provider)
    token_provider = foundry_token_provider()
    if config.provider == "claude":
        from anthropic import AnthropicFoundry

        client = AnthropicFoundry(
            azure_ad_token_provider=token_provider,
            base_url=f"{config.endpoint.rstrip('/')}/anthropic",
        )
        return MessagesAdapter(client, deployment)

    from openai import OpenAI

    client = OpenAI(
        api_key=token_provider(),
        base_url=f"{config.endpoint.rstrip('/')}/openai/v1/",
    )
    return ResponsesAdapter(client, deployment)
