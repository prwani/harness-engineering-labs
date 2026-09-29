"""Canonical model contract plus Foundry Messages and Responses adapters."""

from dataclasses import dataclass, field
import json
from typing import Any, Protocol

from harness.ledger import Usage


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    args: dict[str, Any]
    item_id: str | None = None


@dataclass(frozen=True)
class Turn:
    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    stop: str = "end"
    usage: Usage = field(default_factory=Usage)
    raw: Any = None


class ModelClient(Protocol):
    def complete(
        self, *, system: str, messages: list[dict[str, Any]],
        tools: list[dict[str, Any]], **opts: Any
    ) -> Turn: ...


def _claude_usage(value: Any) -> Usage:
    if not value:
        return Usage()
    return Usage(
        input_tokens=getattr(value, "input_tokens", 0),
        output_tokens=getattr(value, "output_tokens", 0),
        cached_tokens=getattr(value, "cache_read_input_tokens", 0) or 0,
        cache_write_tokens=getattr(value, "cache_creation_input_tokens", 0) or 0,
    )


def _responses_usage(value: Any) -> Usage:
    if not value:
        return Usage()
    details = getattr(value, "input_tokens_details", None)
    return Usage(
        input_tokens=getattr(value, "input_tokens", 0),
        output_tokens=getattr(value, "output_tokens", 0),
        cached_tokens=getattr(details, "cached_tokens", 0) if details else 0,
    )


class MessagesAdapter:
    def __init__(self, client: Any, model: str) -> None:
        self.client, self.model = client, model

    def complete(self, *, system: str, messages: list[dict[str, Any]],
                 tools: list[dict[str, Any]], **opts: Any) -> Turn:
        messages = [
            {
                "role": "user",
                "content": [
                   {
                       "type": "tool_result",
                       "tool_use_id": result["call_id"],
                       "content": result["output"],
                   }
                   for result in message["content"]
                ],
            }
            if message["role"] == "tool"
            else message
            for message in messages
        ]
        tools = [
            {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "input_schema": tool.get("input_schema", {"type": "object"}),
            }
            for tool in tools
        ]
        response = self.client.messages.create(
            model=self.model,
            system=system,
            messages=messages,
            tools=tools,
            max_tokens=opts.pop("max_tokens", 1024),
            **opts,
        )
        calls = [
            ToolCall(block.id, block.name, dict(block.input))
            for block in response.content if block.type == "tool_use"
        ]
        text = "".join(block.text for block in response.content if block.type == "text")
        stop = "tool" if response.stop_reason == "tool_use" else (
            "length" if response.stop_reason == "max_tokens" else "end"
        )
        return Turn(text, calls, stop, _claude_usage(response.usage), response.content)


class ResponsesAdapter:
    def __init__(self, client: Any, model: str) -> None:
        self.client, self.model = client, model

    def complete(self, *, system: str, messages: list[dict[str, Any]],
                 tools: list[dict[str, Any]], **opts: Any) -> Turn:
        inputs = []
        for message in messages:
            if message["role"] == "assistant":
                raw = message["content"]
                inputs.extend(
                   item.model_dump(exclude_none=True) if hasattr(item, "model_dump") else item
                   for item in raw if isinstance(raw, list)
                )
            elif message["role"] == "tool":
                inputs.extend(
                   {
                       "type": "function_call_output",
                       "call_id": result["call_id"],
                       "output": result["output"],
                   }
                   for result in message["content"]
                )
            else:
                inputs.append(message)
        tools = [
            {
                "type": "function",
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool.get("input_schema", {"type": "object"}),
            }
            for tool in tools
        ]
        response = self.client.responses.create(
            model=self.model, instructions=system, input=inputs, tools=tools,
            store=False, **opts
        )
        calls = [
            ToolCall(item.call_id, item.name, json.loads(item.arguments), item.id)
            for item in response.output if item.type == "function_call"
        ]
        text = "".join(
            part.text for item in response.output if item.type == "message"
            for part in item.content if part.type == "output_text"
        )
        stop = "length" if response.status == "incomplete" else ("tool" if calls else "end")
        return Turn(text, calls, stop, _responses_usage(response.usage), response.output)


class ScriptedModel:
    """Deterministic ModelClient for offline checks and CLI fixtures."""

    def __init__(self, turns: list[Turn]) -> None:
        self._turns = iter(turns)

    def complete(self, **_: Any) -> Turn:
        try:
            return next(self._turns)
        except StopIteration as error:
            raise RuntimeError("ScriptedModel ran out of scripted turns") from error
