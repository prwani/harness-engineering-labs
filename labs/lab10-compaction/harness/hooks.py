"""Lifecycle hooks for the tool loop and a deliberately small demo policy."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolDecision:
    allowed: bool
    reason: str = ""


PreToolHook = Callable[[str, dict[str, Any]], ToolDecision]
PreModelHook = Callable[[list[dict[str, Any]]], None]


@dataclass(frozen=True)
class HookPipeline:
    pre_tool: tuple[PreToolHook, ...] = ()
    pre_model: tuple[PreModelHook, ...] = ()

    def before_model(self, messages: list[dict[str, Any]]) -> None:
        for hook in self.pre_model:
            hook(messages)

    def before_tool(self, name: str, args: dict[str, Any]) -> ToolDecision:
        decisions = [hook(name, args) for hook in self.pre_tool]
        for decision in decisions:
            if not decision.allowed:
                if not decision.reason:
                    raise ValueError("Deny decisions must include a reason.")
                return decision
        return ToolDecision(True)


def validate_history(messages: list[dict[str, Any]]) -> None:
    """Each completed tool batch must follow an assistant turn with one result per call."""
    if not messages or messages[0]["role"] != "user":
        raise ValueError("History must start with a user message.")
    if (len(messages) - 1) % 2:
        raise ValueError("History contains an incomplete tool batch.")
    for offset in range(1, len(messages), 2):
        assistant, results = messages[offset:offset + 2]
        if assistant["role"] != "assistant" or results["role"] != "tool":
            raise ValueError("History must alternate assistant calls and tool results.")
        call_ids = assistant["call_ids"]
        result_ids = [result["call_id"] for result in results["content"]]
        if not call_ids or any(not call_id for call_id in call_ids):
            raise ValueError("Tool call IDs must be nonempty.")
        if len(call_ids) != len(set(call_ids)) or result_ids != call_ids:
            raise ValueError("Every tool call must have one result with the same ID.")


_GIT_READS = (["status"], ["log", "-1", "--oneline"])
_AZURE_READS = (["account", "show"], ["resource", "list"])


def read_command_policy(name: str, args: dict[str, Any]) -> ToolDecision:
    if name == "shell":
        return ToolDecision(False, "shell commands are disabled in Lab 2B")
    if name == "git_cli" and args.get("args") not in _GIT_READS:
        return ToolDecision(False, "git_cli permits only status or log -1 --oneline")
    if name == "azure_cli" and args.get("args") not in _AZURE_READS:
        return ToolDecision(False, "azure_cli permits only account show or resource list")
    return ToolDecision(True)
