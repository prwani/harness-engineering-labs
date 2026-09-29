"""Deterministic first-cut tool loop with exactly one result per call."""

from collections.abc import Callable
from typing import Any

from harness.ledger import Usage
from harness.models import Turn
from harness.models.adapters import ModelClient


Tool = Callable[[dict[str, Any]], str]


def run_tool_loop(
    client: ModelClient,
    task: str,
    system: str,
    tools: dict[str, Tool],
    max_iterations: int = 3,
    tool_definitions: list[dict[str, Any]] | None = None,
    on_tool_call: Callable[[str, dict[str, Any]], None] | None = None,
) -> Turn:
    messages: list[dict[str, Any]] = [{"role": "user", "content": task}]
    total_usage = Usage()
    for _ in range(max_iterations):
        turn = client.complete(
            system=system,
            messages=messages,
            tools=tool_definitions or [{"name": name} for name in tools],
        )
        total_usage = Usage(
            input_tokens=total_usage.input_tokens + turn.usage.input_tokens,
            output_tokens=total_usage.output_tokens + turn.usage.output_tokens,
            cached_tokens=total_usage.cached_tokens + turn.usage.cached_tokens,
            cache_write_tokens=total_usage.cache_write_tokens + turn.usage.cache_write_tokens,
        )
        if not turn.tool_calls:
            return Turn(
                turn.text,
                turn.tool_calls,
                turn.stop,
                total_usage,
                turn.raw,
            )
        messages.append({"role": "assistant", "content": turn.raw or turn.text})
        results = []
        for call in turn.tool_calls:
            if on_tool_call:
                on_tool_call(call.name, call.args)
            tool = tools.get(call.name)
            try:
                output = tool(call.args) if tool else f"ERROR: unknown tool {call.name}"
            except Exception as error:
                output = f"ERROR: {error}"
            results.append({"call_id": call.id, "output": output})
        messages.append({"role": "tool", "content": results})
    raise RuntimeError("tool loop reached max_iterations")
