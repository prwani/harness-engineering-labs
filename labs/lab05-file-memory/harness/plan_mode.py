"""Plan mode for `harness ask`: investigate and plan with no way to edit.

Plan mode and execute mode are two tool envelopes on one harness. In plan
mode the write tools are not offered to the model at all, and a ``pre_tool``
policy denies anything that could change the repository, so a plan cannot
"accidentally" start the work. Only the human switches modes (``--plan``,
``/plan``, ``/execute``); there is no tool the model can call to do it.

Todos are harness-owned state. The model changes them only through the
``write_todos`` tool; the harness shows them with ``/todos``, saves them
next to the session and reminds the model of open items on every question.
"""

from dataclasses import asdict
import json
from pathlib import Path
from typing import Any

from harness.hooks import ToolDecision
from harness.todos import Todo, TodoList

PLAN_TOOLS = frozenset({
    "list_files", "read_file", "git_status", "git_log", "git_cli", "run_tests", "write_todos",
})
# Git subcommands that only read. `branch` and `tag` only list when given no names.
READ_ONLY_GIT = frozenset({
    "status", "diff", "log", "show", "describe", "ls-files", "grep", "blame",
    "rev-parse", "shortlog",
})

PLAN_PROMPT = (
    "You are in PLAN MODE. Do not change anything: write tools are not available "
    "and edits are denied. Investigate the code, then reply with a concrete plan: "
    "the files you will change, the steps in order, and every test you will add. "
    "Record the steps with write_todos. The human reviews the plan; only the human "
    "can switch to execute mode."
)
EXECUTE_PROMPT = (
    "Work through the open todos in order. After finishing each one, call write_todos "
    "with the full list and that item marked done."
)


def plan_mode_policy(name: str, args: dict[str, Any]) -> ToolDecision:
    """pre_tool policy for plan mode: read-only tools and read-only Git only."""
    if name not in PLAN_TOOLS:
        return ToolDecision(False, f"plan mode: {name} is not available until the human approves the plan")
    if name == "git_cli":
        argv = [str(value) for value in args.get("args") or []]
        subcommand = argv[0] if argv else ""
        names = [value for value in argv[1:] if not value.startswith("-")]
        if subcommand in {"branch", "tag"} and not names:
            return ToolDecision(True)
        if subcommand not in READ_ONLY_GIT:
            return ToolDecision(False, f"plan mode: git {subcommand} could change the repository")
    return ToolDecision(True)


def render_todos(todos: TodoList) -> str:
    if not todos.items:
        return "No todos."
    return "\n".join(f"[{'x' if item.done else ' '}] {item.text}" for item in todos.items)


def load_todos(path: Path) -> TodoList:
    if not path.is_file():
        return TodoList()
    return TodoList([Todo(**item) for item in json.loads(path.read_text(encoding="utf-8"))])


def save_todos(todos: TodoList, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([asdict(item) for item in todos.items], indent=2), encoding="utf-8")


def todo_tool(todos: TodoList, on_change=None):
    """The `write_todos` tool and its definition; it replaces the whole list."""

    def write_todos(args: dict[str, Any]) -> str:
        items = args.get("todos")
        if not isinstance(items, list) or not all(isinstance(item, dict) and item.get("text") for item in items):
            raise ValueError("todos must be a list of {text, done} objects")
        todos.items = [Todo(str(item["text"]), bool(item.get("done", False))) for item in items]
        if on_change:
            on_change(todos)
        return "Todos updated:\n" + render_todos(todos)

    definition = {
        "name": "write_todos",
        "description": "Replace the todo list for this task. Send every item each time; "
                       "mark finished items done.",
        "input_schema": {
            "type": "object",
            "properties": {
                "todos": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"text": {"type": "string"}, "done": {"type": "boolean"}},
                        "required": ["text"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["todos"],
            "additionalProperties": False,
        },
    }
    return write_todos, definition


def mode_prompt(mode: str, todos: TodoList | None) -> str:
    """System-prompt addition for the current mode, plus the open-todo reminder."""
    parts = [PLAN_PROMPT if mode == "plan" else ""]
    if todos is not None and todos.open:
        if mode != "plan":
            parts.append(EXECUTE_PROMPT)
        parts.append(todos.reminder())
    return "\n\n".join(part for part in parts if part)
