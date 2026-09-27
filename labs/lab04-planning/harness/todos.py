"""Harness-owned todo state, shared across planner and executor turns."""

from dataclasses import dataclass, field


@dataclass
class Todo:
    text: str
    done: bool = False


@dataclass
class TodoList:
    """The harness owns this list; agents can only read or mutate it through
    the ``write_todos`` tool, never by editing the harness state directly."""

    items: list[Todo] = field(default_factory=list)

    def write(self, texts: list[str]) -> None:
        self.items = [Todo(text=text) for text in texts]

    def complete(self, text: str) -> None:
        for item in self.items:
            if item.text == text:
                item.done = True
                return
        raise ValueError(f"no such todo: {text}")

    @property
    def open(self) -> list[Todo]:
        return [item for item in self.items if not item.done]

    def reminder(self) -> str | None:
        """Rendered every turn by the ``pre_model`` hook so open todos are
        never silently dropped from context."""
        if not self.open:
            return None
        lines = "\n".join(f"- {item.text}" for item in self.open)
        return f"Open todos:\n{lines}"
