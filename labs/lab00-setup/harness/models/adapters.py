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


def _usage(value: Any, *, claude: bool) -> Usage:
    if not value:
        return Usage()
    if claude:
        return Usage(
            input_tokens=getattr(value, "input_tokens", 0),
            output_tokens=getattr(value, "output_tokens", 0),
            cached_tokens=getattr(value, "cache_read_input_tokens", 0) or 0,
            cache_write_tokens=getattr(value, "cache_creation_input_tokens", 0) or 0,
        )
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
        response = self.client.messages.create(
            model=self.model, system=system, messages=messages, tools=tools, **opts
        )
        calls = [
            ToolCall(block.id, block.name, dict(block.input))
            for block in response.content if block.type == "tool_use"
        ]
        text = "".join(block.text for block in response.content if block.type == "text")
        stop = "tool" if response.stop_reason == "tool_use" else (
            "length" if response.stop_reason == "max_tokens" else "end"
        )
        return Turn(text, calls, stop, _usage(response.usage, claude=True), response.content)


class ResponsesAdapter:
    def __init__(self, client: Any, model: str) -> None:
        self.client, self.model = client, model

    def complete(self, *, system: str, messages: list[dict[str, Any]],
                 tools: list[dict[str, Any]], **opts: Any) -> Turn:
        response = self.client.responses.create(
            model=self.model, instructions=system, input=messages, tools=tools,
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
        stop = "tool" if calls else ("length" if response.status == "incomplete" else "end")
        return Turn(text, calls, stop, _usage(response.usage, claude=False), response.output)


class ScriptedModel:
    """Deterministic ModelClient for offline checks and CLI fixtures."""

    def __init__(self, turns: list[Turn]) -> None:
        self._turns = iter(turns)

    def complete(self, **_: Any) -> Turn:
        return next(self._turns)
