"""Permission rules for `harness ask`: allow, ask or deny each tool call.

Rules are written ``tool`` or ``tool(pattern)`` and live in the
``permissions`` section of three settings files, broadest first:

- user:    ``$HARNESS_HOME/settings.json`` (default ``~/.harness``)
- project: ``.harness/settings.json``, committed with the code
- local:   ``.harness/settings.local.json``, personal and gitignored

The pattern is a glob matched against the call's *subject*: the project-
relative path for file tools, the arguments joined by spaces for
``git_cli`` (``git_cli(commit *)``), and the JSON arguments otherwise.

For each call, the most restrictive matching rule wins: deny, then ask,
then allow. With no matching rule the default applies: reads run, edits and
Git commands that are not read-only ask. An "always" answer at the prompt
allows that exact call for the rest of the session, but never overrides a
deny or an explicit ask rule.

Rules match a tool and its arguments; they are not a sandbox. A different
tool that reaches the same data is a different rule.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from fnmatch import fnmatchcase
import json
from pathlib import Path
import re
from typing import Any

from harness.approval import Decision
from harness.hooks import ToolDecision
from harness.plan_mode import READ_ONLY_GIT
from harness.session import harness_home

READ_TOOLS = frozenset({"list_files", "read_file", "git_status", "git_log", "run_tests", "write_todos"})
EDIT_TOOLS = frozenset({"write_file", "edit_file"})
_RULE = re.compile(r"^([A-Za-z0-9_*?\[\]-]+)(?:\((.*)\))?$")

# Answers to an "ask": yes once, no, or always for this exact call in this session.
Approver = Callable[[str, dict[str, Any], str], str]
PermissionEvent = Callable[[str, dict[str, Any], str, str], None]


@dataclass(frozen=True)
class PermissionRule:
    decision: Decision
    tool: str
    pattern: str | None
    source: str

    @classmethod
    def parse(cls, text: str, decision: Decision, source: str) -> "PermissionRule":
        match = _RULE.match(text.strip())
        if not match:
            raise ValueError(f"invalid permission rule {text!r} in {source}; use tool or tool(pattern)")
        return cls(decision, match.group(1), match.group(2), source)

    def matches(self, tool: str, subject: str) -> bool:
        if not fnmatchcase(tool, self.tool):
            return False
        return self.pattern is None or fnmatchcase(subject, self.pattern)

    def __str__(self) -> str:
        return self.tool if self.pattern is None else f"{self.tool}({self.pattern})"


def subject(repo: Path, tool: str, args: dict[str, Any]) -> str:
    """The text a rule's pattern is matched against."""
    if "path" in args:
        raw = str(args["path"]).replace("\\", "/")
        root = repo.resolve()
        try:
            return (root / raw).resolve().relative_to(root).as_posix()
        except ValueError:
            return raw
    if isinstance(args.get("args"), list):
        return " ".join(str(value) for value in args["args"])
    return json.dumps(args, sort_keys=True)


def settings_paths(repo: Path) -> list[tuple[str, Path]]:
    return [
        ("user", harness_home() / "settings.json"),
        ("project", repo / ".harness" / "settings.json"),
        ("local", repo / ".harness" / "settings.local.json"),
    ]


def load_rules(repo: Path) -> list[PermissionRule]:
    rules = []
    for scope, path in settings_paths(repo):
        if not path.is_file():
            continue
        try:
            permissions = json.loads(path.read_text(encoding="utf-8")).get("permissions", {})
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid {path}: {error}") from error
        for decision in Decision:
            for text in permissions.get(decision.value, []):
                rules.append(PermissionRule.parse(text, decision, f"{scope} {path}"))
    return rules


def default_decision(tool: str, args: dict[str, Any], *, accept_edits: bool = False) -> Decision:
    if tool in READ_TOOLS:
        return Decision.ALLOW
    if tool in EDIT_TOOLS:
        return Decision.ALLOW if accept_edits else Decision.ASK
    if tool == "git_cli":
        argv = [str(value) for value in args.get("args") or []]
        names = [value for value in argv[1:] if not value.startswith("-")]
        if argv and (argv[0] in READ_ONLY_GIT or (argv[0] in {"branch", "tag"} and not names)):
            return Decision.ALLOW
    return Decision.ASK


@dataclass
class Permissions:
    repo: Path
    rules: list[PermissionRule] = field(default_factory=list)
    accept_edits: bool = False
    session_allowed: set[tuple[str, str]] = field(default_factory=set)

    @classmethod
    def load(cls, repo: Path, *, accept_edits: bool = False) -> "Permissions":
        return cls(repo, load_rules(repo), accept_edits)

    def decide(self, tool: str, args: dict[str, Any]) -> tuple[Decision, str]:
        """The decision for one call and why: a rule, a session approval or the default."""
        text = subject(self.repo, tool, args)
        matching = [rule for rule in self.rules if rule.matches(tool, text)]
        for decision in (Decision.DENY, Decision.ASK):
            for rule in matching:
                if rule.decision is decision:
                    return decision, f"{decision.value} rule {rule} ({rule.source})"
        if (tool, text) in self.session_allowed:
            return Decision.ALLOW, "approved always for this session"
        for rule in matching:
            return Decision.ALLOW, f"allow rule {rule} ({rule.source})"
        decision = default_decision(tool, args, accept_edits=self.accept_edits)
        return decision, f"default: {decision.value}"

    def hook(self, approver: Approver | None = None, on_permission: PermissionEvent | None = None):
        """A pre_tool hook. ``approver`` asks the human; without one, ask means deny."""

        def check(tool: str, args: dict[str, Any]) -> ToolDecision:
            decision, why = self.decide(tool, args)
            if decision is Decision.ASK:
                answer = approver(tool, args, why) if approver else "n"
                if answer == "a" and not why.startswith("ask rule"):
                    self.session_allowed.add((tool, subject(self.repo, tool, args)))
                decision = Decision.ALLOW if answer in {"y", "a"} else Decision.DENY
                why = f"{why}; human answered {'yes' if decision is Decision.ALLOW else 'no'}" \
                    if approver else f"{why}; no one to approve in this run"
            if on_permission:
                on_permission(tool, args, decision.value, why)
            if decision is Decision.DENY:
                return ToolDecision(False, f"permission denied: {why}. Do not retry or work around it; "
                                           "tell the user what you needed.")
            return ToolDecision(True)

        return check

    def describe(self) -> str:
        """What `/permissions` prints."""
        lines = [f"{rule.decision.value:<5} {rule}  [{rule.source}]" for rule in self.rules]
        lines += [f"allow {tool}({text})  [this session]" for tool, text in sorted(self.session_allowed)]
        edits = "allow (--accept-edits)" if self.accept_edits else "ask"
        lines.append(f"Defaults: reads and read-only git allow; write_file/edit_file {edits}; "
                     "everything else ask.")
        return "\n".join(lines)
