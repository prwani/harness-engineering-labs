"""One conversation with the harness: a saved session plus per-question settings.

The CLI renders; this class decides what each question runs with. Every
question goes through the same hooked tool loop as Lab 2B, with the
session's history, and each new message is saved as it happens.
"""

from collections.abc import Callable
from dataclasses import dataclass, fields
from pathlib import Path
from typing import TYPE_CHECKING, Any

from harness.learner import ask_with_tools
from harness.models.adapters import ModelClient, Turn
from harness.session import Session

if TYPE_CHECKING:
    from harness.tool_loop import LoopStats


@dataclass
class Events:
    """Optional callbacks the CLI uses to show progress."""

    on_tool_call: Callable[[str, dict[str, Any]], None] | None = None
    on_hook_denial: Callable[[str, str], None] | None = None
    on_hook_feedback: Callable[[str, str], None] | None = None
    on_model_call: Callable[[int], None] | None = None

    def as_kwargs(self) -> dict[str, Any]:
        return {item.name: getattr(self, item.name) for item in fields(self)}


class Chat:
    def __init__(self, client: ModelClient, repo: Path, session: Session) -> None:
        self.client, self.repo, self.session = client, repo, session

    def ask(self, question: str, events: Events | None = None,
            stats: "LoopStats | None" = None) -> Turn:
        return ask_with_tools(
            self.client,
            question,
            repo=self.repo,
            stats=stats,
            history=self.session.messages,
            on_message=self.session.save,
            **(events or Events()).as_kwargs(),
        )

    def questions(self) -> list[str]:
        return [message["content"] for message in self.session.messages
                if message["role"] == "user" and isinstance(message["content"], str)]
