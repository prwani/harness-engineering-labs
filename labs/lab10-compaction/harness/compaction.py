"""Context compaction policy, summary handoff artifact, and repository map
metadata.

When the transcript's estimated token count crosses a threshold, the
``pre_model`` hook triggers compaction: older messages are replaced by a
summary handoff artifact, and the most recent messages are kept verbatim so
the model never loses immediate context. A repository map gives the model
a cheap, stable index of the sandboxed repo instead of re-reading files.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def estimate_tokens(messages: list[dict[str, Any]]) -> int:
    """Rough token estimate: ~4 characters per token."""
    return sum(len(str(message.get("content", ""))) for message in messages) // 4


@dataclass(frozen=True)
class CompactionPolicy:
    token_threshold: int
    keep_recent: int = 4

    def should_compact(self, messages: list[dict[str, Any]]) -> bool:
        return estimate_tokens(messages) > self.token_threshold and len(messages) > self.keep_recent


@dataclass(frozen=True)
class SummaryHandoff:
    """The artifact that replaces compacted messages: a short summary plus
    what it dropped, so a human or later turn can tell what was lost."""

    summary: str
    dropped_message_count: int
    kept_recent: tuple[dict[str, Any], ...]


def summarize(messages: list[dict[str, Any]]) -> str:
    parts = []
    for message in messages:
        content = message.get("content", "")
        parts.append(f"{message.get('role', 'unknown')}: {str(content)[:80]}")
    return " | ".join(parts)


def compact(policy: CompactionPolicy, messages: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], SummaryHandoff | None]:
    """Return the (possibly compacted) messages and the handoff artifact, if any."""
    if not policy.should_compact(messages):
        return messages, None
    recent = messages[-policy.keep_recent:]
    dropped = messages[: -policy.keep_recent]
    handoff = SummaryHandoff(
        summary=summarize(dropped), dropped_message_count=len(dropped), kept_recent=tuple(recent)
    )
    new_messages = [{"role": "system", "content": f"[compacted] {handoff.summary}"}, *recent]
    return new_messages, handoff


@dataclass(frozen=True)
class RepoMapEntry:
    path: str
    kind: str  # "file" or "dir"


def build_repo_map(root: Path) -> list[RepoMapEntry]:
    """A stable, cheap index of the sandboxed repo, offered instead of
    letting the model re-read directories every turn."""
    entries: list[RepoMapEntry] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        entries.append(RepoMapEntry(path=relative, kind="dir" if path.is_dir() else "file"))
    return entries
