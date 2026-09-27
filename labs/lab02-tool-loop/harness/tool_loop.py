"""Deterministic first-cut tool loop with exactly one result per call."""

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
        results = []
        for call in turn.tool_calls:
            tool = tools.get(call.name)
            output = tool(call.args) if tool else f"ERROR: unknown tool {call.name}"
            results.append({"call_id": call.id, "output": output})
        messages.append({"role": "tool", "content": results})
    raise RuntimeError("tool loop reached max_iterations")
