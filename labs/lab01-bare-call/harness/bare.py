"""Stateless, tool-free model execution for Lab 1."""

from harness.models import Turn
from harness.models.adapters import ModelClient


def run_bare(client: ModelClient, task: str, system: str) -> Turn:
    """Send one task without exposing tools or preserving history."""
    return client.complete(
        system=system,
        messages=[{"role": "user", "content": task}],
        tools=[],
    )
