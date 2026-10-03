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
from harness.permissions import Approver, PermissionEvent, Permissions, load_rules
from harness.plan_mode import load_todos, save_todos
from harness.session import Session
from harness.todos import TodoList

if TYPE_CHECKING:
    from harness.tool_loop import LoopStats


@dataclass
class Events:
    """Optional callbacks the CLI uses to show progress."""

    on_tool_call: Callable[[str, dict[str, Any]], None] | None = None
    on_hook_denial: Callable[[str, str], None] | None = None
    on_hook_feedback: Callable[[str, str], None] | None = None
    on_model_call: Callable[[int], None] | None = None
    approver: Approver | None = None
    on_permission: PermissionEvent | None = None

    def as_kwargs(self) -> dict[str, Any]:
        return {item.name: getattr(self, item.name) for item in fields(self)}


APPROVED = "The plan is approved. Implement it now and keep the todo list up to date."


class Chat:
    def __init__(self, client: ModelClient, repo: Path, session: Session,
                 *, mode: str = "execute", accept_edits: bool = False) -> None:
        self.client, self.repo, self.session = client, repo, session
        self.set_mode(mode)
        self.permissions = Permissions.load(repo, accept_edits=accept_edits)
        # Todos are harness state, saved next to the session file.
        self.todos_path = session.path.with_suffix(".todos.json") if session.path else None
        self.todos = load_todos(self.todos_path) if self.todos_path else TodoList()

    def set_mode(self, mode: str) -> None:
        """Only the human (through the CLI) calls this; no tool can."""
        if mode not in {"plan", "execute"}:
            raise ValueError(f"unknown mode: {mode}")
        self.mode = mode

    def _save_todos(self, todos: TodoList) -> None:
        if self.todos_path:
            save_todos(todos, self.todos_path)

    def ask(self, question: str, events: Events | None = None,
            stats: "LoopStats | None" = None) -> Turn:
        # Settings are reread for every question; session approvals are kept.
        self.permissions.rules = load_rules(self.repo)
        return ask_with_tools(
            self.client,
            question,
            repo=self.repo,
            stats=stats,
            history=self.session.messages,
            on_message=self.session.save,
            mode=self.mode,
            todos=self.todos,
            on_todos=self._save_todos,
            permissions=self.permissions,
            **(events or Events()).as_kwargs(),
        )

    def questions(self) -> list[str]:
        return [message["content"] for message in self.session.messages
                if message["role"] == "user" and isinstance(message["content"], str)]
