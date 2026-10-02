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


# --- /compact in `harness ask` -------------------------------------------------

COMPACT_SYSTEM = (
    "You summarize a coding-agent conversation so it can continue from the summary "
    "alone. Do not call tools."
)
COMPACT_REQUEST = (
    "Summarize this conversation so far. The summary replaces the whole conversation: "
    "anything you leave out is gone. Keep the user's goals and decisions, facts found "
    "with their evidence (file names, identifiers, values), files changed, and open "
    "tasks. Drop raw tool output."
)
SUMMARY_HEADER = "This conversation was compacted. Summary of everything before this point:"
SUMMARY_ACK = "Understood. I'll continue from this summary."


def compact_request(instructions: str = "") -> str:
    extra = f"\n\nInstructions from the user for this summary: {instructions}" if instructions else ""
    return COMPACT_REQUEST + extra


def summary_messages(summary: str) -> list[dict[str, Any]]:
    """The new history: the summary as a user message, acknowledged by the assistant."""
    return [{"role": "user", "content": f"{SUMMARY_HEADER}\n\n{summary}"},
            {"role": "assistant", "content": SUMMARY_ACK}]


def summarize_history(client: Any, messages: list[dict[str, Any]], tools: list[dict[str, Any]],
                      instructions: str = "") -> str:
    """Ask the model for the summary. Tool definitions are still sent because the
    history contains tool calls, which some providers reject without them."""
    request = [{key: value for key, value in message.items() if key != "call_ids"}
               for message in messages]
    request.append({"role": "user", "content": compact_request(instructions)})
    turn = client.complete(system=COMPACT_SYSTEM, messages=request, tools=tools)
    if not turn.text.strip():
        raise RuntimeError("the model returned no summary; the history is unchanged")
    return turn.text.strip()


def history_tokens(messages: list[dict[str, Any]]) -> int:
    """About 4 characters per token, counting tool calls and results."""
    import json

    return sum(len(json.dumps(message.get("content", ""), default=str)) for message in messages) // 4
