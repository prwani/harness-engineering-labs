"""Deterministic first-cut tool loop with exactly one result per call."""

from collections.abc import Callable
from dataclasses import dataclass
from time import perf_counter
from typing import Any

from harness.ledger import Usage
from harness.models import Turn
from harness.models.adapters import ModelClient


Tool = Callable[[dict[str, Any]], str]


@dataclass
class LoopStats:
    """Counts and wall-clock time for one run of the tool loop."""

    model_calls: int = 0
    tool_calls: int = 0
    tool_errors: int = 0
    model_seconds: float = 0.0
    tool_seconds: float = 0.0


def run_tool_loop(
    client: ModelClient,
    task: str,
    system: str,
    tools: dict[str, Tool],
    max_iterations: int = 3,
    tool_definitions: list[dict[str, Any]] | None = None,
    on_tool_call: Callable[[str, dict[str, Any]], None] | None = None,
    on_model_call: Callable[[int], None] | None = None,
    stats: LoopStats | None = None,
) -> Turn:
    messages: list[dict[str, Any]] = [{"role": "user", "content": task}]
    stats = stats if stats is not None else LoopStats()
    total_usage = Usage()
    for _ in range(max_iterations):
        stats.model_calls += 1
        if on_model_call:
            on_model_call(stats.model_calls)
        started = perf_counter()
        try:
            turn = client.complete(
                system=system,
                messages=messages,
                tools=tool_definitions or [{"name": name} for name in tools],
            )
        finally:
            stats.model_seconds += perf_counter() - started
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
            stats.tool_calls += 1
            if on_tool_call:
                on_tool_call(call.name, call.args)
            started = perf_counter()
            try:
                if (tool := tools.get(call.name)) is None:
                    output = f"ERROR: unknown tool {call.name}"
                    stats.tool_errors += 1
                else:
                    output = tool(call.args)
            except Exception as error:
                output = f"ERROR: {error}"
                stats.tool_errors += 1
            stats.tool_seconds += perf_counter() - started
            results.append({"call_id": call.id, "output": output})
        messages.append({"role": "tool", "content": results})
    raise RuntimeError("tool loop reached max_iterations")
