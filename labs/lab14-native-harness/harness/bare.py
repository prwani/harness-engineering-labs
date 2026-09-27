"""Stateless, tool-free model execution retained from Lab 1."""

from harness.models import Turn
from harness.models.adapters import ModelClient


def run_bare(client: ModelClient, task: str, system: str) -> Turn:
    return client.complete(
        system=system,
        messages=[{"role": "user", "content": task}],
        tools=[],
    )
