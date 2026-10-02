"""Lifecycle hooks for the tool loop: built-in policy, project hooks, and scoped rules."""

from collections.abc import Callable
from dataclasses import dataclass
from fnmatch import fnmatch
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


@dataclass(frozen=True)
class ToolDecision:
    allowed: bool
    reason: str = ""


PreToolHook = Callable[[str, dict[str, Any]], ToolDecision]
PreModelHook = Callable[[list[dict[str, Any]]], None]
PostToolHook = Callable[[str, dict[str, Any], str], str]
HookFeedback = Callable[[str, str], None]


@dataclass(frozen=True)
class HookPipeline:
    pre_tool: tuple[PreToolHook, ...] = ()
    pre_model: tuple[PreModelHook, ...] = ()
    post_tool: tuple[PostToolHook, ...] = ()

    def before_model(self, messages: list[dict[str, Any]]) -> None:
        for hook in self.pre_model:
            hook(messages)

    def before_tool(self, name: str, args: dict[str, Any]) -> ToolDecision:
        for hook in self.pre_tool:
            decision = hook(name, args)
            if not decision.allowed:
                if not decision.reason:
                    raise ValueError("Deny decisions must include a reason.")
                return decision
        return ToolDecision(True)

    def after_tool(self, name: str, args: dict[str, Any], output: str) -> str:
        for hook in self.post_tool:
            output = hook(name, args, output)
        return output


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


# Teaching policy, not a sandbox: deny the Git subcommands that discard work,
# rewrite history, publish, or change configuration; allow everyday ones.
_GIT_DENIED = frozenset({
    "rm", "reset", "clean", "push", "rebase", "checkout", "restore", "apply",
    "config", "filter-branch", "update-ref", "gc", "worktree",
})
_AZURE_READS = (["account", "show"], ["resource", "list"])


def command_policy(name: str, args: dict[str, Any]) -> ToolDecision:
    """Built-in pre-tool policy that project hooks can tighten but never loosen."""
    if name == "shell":
        return ToolDecision(False, "shell commands are disabled; use run_tests, git_cli, and file tools")
    if name == "git_cli":
        argv = args.get("args")
        if not isinstance(argv, list) or not argv or str(argv[0]).startswith("-"):
            return ToolDecision(False, "git_cli needs a subcommand first; global options are not allowed")
        if str(argv[0]) in _GIT_DENIED:
            return ToolDecision(False, f"git {argv[0]} is denied by the built-in policy")
    if name == "azure_cli" and args.get("args") not in _AZURE_READS:
        return ToolDecision(False, "azure_cli permits only account show or resource list")
    return ToolDecision(True)


@dataclass(frozen=True)
class Rule:
    name: str
    paths: tuple[str, ...]
    text: str

    def applies_to(self, path: str) -> bool:
        return not self.paths or any(fnmatch(path, pattern) for pattern in self.paths)


def load_rules(root: Path) -> list[Rule]:
    """Read `.harness/rules/*.md`; optional `paths:` front matter scopes each rule.

    `paths` accepts a comma-separated value or a YAML-style `- item` list of globs.
    A rule without `paths` applies to the first file the agent touches.
    """
    rules = []
    for file in sorted((root / ".harness" / "rules").glob("*.md")):
        text = file.read_text(encoding="utf-8")
        paths: tuple[str, ...] = ()
        match = re.match(r"---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
        if match:
            in_paths = False
            for line in match.group(1).splitlines():
                key, _, value = line.partition(":")
                if in_paths and line.strip().startswith("- "):
                    paths += (line.strip()[2:].strip().strip("'\""),)
                    continue
                in_paths = key.strip() == "paths"
                if in_paths:
                    paths += tuple(item.strip().strip("'\"") for item in value.split(",") if item.strip())
            text = text[match.end():]
        rules.append(Rule(file.name, paths, text.strip()))
    return rules


def _rules_hook(root: Path, rules: list[Rule], on_feedback: HookFeedback | None) -> PostToolHook:
    loaded: set[str] = set()

    def hook(name: str, args: dict[str, Any], output: str) -> str:
        if "path" not in args or name not in {"read_file", "write_file", "edit_file"}:
            return output
        try:
            path = (root / str(args["path"])).resolve().relative_to(root).as_posix()
        except ValueError:
            return output
        for rule in rules:
            if rule.name in loaded or not rule.applies_to(path):
                continue
            loaded.add(rule.name)
            if on_feedback:
                on_feedback(name, f"loaded rule {rule.name} for {path}")
            output += f"\n\nProject rule {rule.name} applies to {path}:\n{rule.text}"
        return output

    return hook


def _command(root: Path, entry: dict[str, Any]) -> tuple[re.Pattern[str], list[str]]:
    command = entry.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(p, str) for p in command):
        raise ValueError("Each hook needs a non-empty 'command' list of strings.")
    if command[0] in {"python", "python3"}:
        command = [sys.executable, *command[1:]]
    return re.compile(str(entry.get("matcher", ".*"))), command


def _run_hook(root: Path, command: list[str], payload: dict[str, Any], timeout: int):
    return subprocess.run(
        command, cwd=root, input=json.dumps(payload), capture_output=True,
        text=True, check=False, timeout=timeout,
    )


def _pre_command_hook(root: Path, entry: dict[str, Any]) -> PreToolHook:
    matcher, command = _command(root, entry)

    def hook(name: str, args: dict[str, Any]) -> ToolDecision:
        if not matcher.fullmatch(name):
            return ToolDecision(True)
        result = _run_hook(root, command, {"event": "pre_tool", "tool": name, "args": args, "cwd": str(root)}, 30)
        if result.returncode == 2:
            return ToolDecision(False, result.stderr.strip() or f"blocked by {command[-1]}")
        return ToolDecision(True)

    return hook


def _post_command_hook(root: Path, entry: dict[str, Any], on_feedback: HookFeedback | None) -> PostToolHook:
    matcher, command = _command(root, entry)

    def hook(name: str, args: dict[str, Any], output: str) -> str:
        if not matcher.fullmatch(name):
            return output
        payload = {"event": "post_tool", "tool": name, "args": args, "cwd": str(root),
                   "output": output[:4_000]}
        try:
            result = _run_hook(root, command, payload, 120)
        except (OSError, subprocess.TimeoutExpired) as error:
            message = f"{command[-1]} could not run: {error}"
        else:
            message = (result.stderr if result.returncode == 2 else result.stdout).strip()
            if result.returncode == 2:
                message = message or f"{command[-1]} reported a problem"
                output += f"\n\nPost-tool hook feedback ({command[-1]}):\n{message[-4_000:]}"
        if message and on_feedback:
            on_feedback(name, message.splitlines()[0])
        return output

    return hook


def load_project_hooks(repo: Path, on_feedback: HookFeedback | None = None) -> HookPipeline:
    """Build hooks from `.harness/settings.json` and `.harness/rules/` in the project.

    Project hooks are commands, like Claude Code hooks: they receive the tool call as
    JSON on stdin. A pre_tool hook that exits with code 2 blocks the call (stderr is the
    reason). A post_tool hook that exits with code 2 sends its stderr back to the model.
    """
    root = repo.resolve()
    settings_file = root / ".harness" / "settings.json"
    settings = {}
    if settings_file.is_file():
        try:
            settings = json.loads(settings_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid {settings_file}: {error}") from error
    hooks = settings.get("hooks", {})
    pre_tool = tuple(_pre_command_hook(root, entry) for entry in hooks.get("pre_tool", []))
    post_tool = [_post_command_hook(root, entry, on_feedback) for entry in hooks.get("post_tool", [])]
    if rules := load_rules(root):
        post_tool.insert(0, _rules_hook(root, rules, on_feedback))
    return HookPipeline(pre_tool=pre_tool, post_tool=tuple(post_tool))


__all__ = [
    "HookPipeline", "Rule", "ToolDecision", "command_policy", "load_project_hooks",
    "load_rules", "validate_history",
]
