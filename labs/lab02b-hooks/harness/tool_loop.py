"""Deterministic first-cut tool loop with exactly one result per call."""

from collections.abc import Callable
from typing import Any

from harness.ledger import Usage
from harness.hooks import HookPipeline, read_command_policy, validate_history
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
    hooks: HookPipeline | None = None,
    on_hook_denial: Callable[[str, str], None] | None = None,
) -> Turn:
    messages: list[dict[str, Any]] = [{"role": "user", "content": task}]
    pipeline = HookPipeline(
        pre_tool=(*(hooks.pre_tool if hooks else ()), read_command_policy),
        pre_model=(*(hooks.pre_model if hooks else ()), validate_history),
    )
    total_usage = Usage()
    for _ in range(max_iterations):
        pipeline.before_model(messages)
        turn = client.complete(
            system=system,
            messages=[{key: value for key, value in message.items() if key != "call_ids"}
                      for message in messages],
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
        call_ids = [call.id for call in turn.tool_calls]
        if not all(call_ids) or len(call_ids) != len(set(call_ids)):
            raise ValueError("Tool call IDs must be nonempty and unique per turn.")
        messages.append({
            "role": "assistant",
            "content": turn.raw or turn.text,
            "call_ids": call_ids,
        })
        results = []
        for call in turn.tool_calls:
            if on_tool_call:
                on_tool_call(call.name, call.args)
            try:
                decision = pipeline.before_tool(call.name, call.args)
                if not decision.allowed:
                    output = f"DENIED: {decision.reason}"
                    if on_hook_denial:
                        on_hook_denial(call.name, decision.reason)
                else:
                    tool = tools.get(call.name)
                    output = tool(call.args) if tool else f"ERROR: unknown tool {call.name}"
            except Exception as error:
                output = f"ERROR: {error}"
            results.append({"call_id": call.id, "output": output})
        messages.append({"role": "tool", "content": results})
    raise RuntimeError("tool loop reached max_iterations")
