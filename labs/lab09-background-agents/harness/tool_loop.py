"""Deterministic first-cut tool loop retained from Lab 2."""

from collections.abc import Callable
from typing import Any

from harness.models import Turn
from harness.models.adapters import ModelClient

Tool = Callable[[dict[str, Any]], str]


def run_tool_loop(
    client: ModelClient, task: str, system: str, tools: dict[str, Tool], max_iterations: int = 3
) -> Turn:
    messages: list[dict[str, Any]] = [{"role": "user", "content": task}]
    for _ in range(max_iterations):
        turn = client.complete(system=system, messages=messages, tools=[])
        if not turn.tool_calls:
            return turn
        messages.append({"role": "tool", "content": [
            {"call_id": call.id, "output": tools[call.name](call.args)}
            if call.name in tools else {"call_id": call.id, "output": f"ERROR: unknown tool {call.name}"}
            for call in turn.tool_calls
        ]})
    raise RuntimeError("tool loop reached max_iterations")
