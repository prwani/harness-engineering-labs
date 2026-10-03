"""Run learner questions with the capabilities available in this snapshot."""

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

from harness.bare import run_bare
from harness.models.adapters import ModelClient, Turn

MAX_ITERATIONS = 30
SYSTEM_PROMPT = (
    "You are a coding agent working in the selected working directory. Read files "
    "before changing them, use write_file and edit_file for edits, run_tests to "
    "check your work, and git_cli for version control. Hooks enforce policy: shell "
    "is denied, destructive Git commands are denied, and project hooks may block "
    "a call or add feedback to its result. A denied call did not run; do not work "
    "around a denial. Follow any project rule included in a tool result, and do "
    "not claim success without evidence."
)

if TYPE_CHECKING:
    from harness.permissions import Approver, PermissionEvent, Permissions
    from harness.todos import TodoList
    from harness.tool_loop import LoopStats


def ask_with_tools(
    client: ModelClient,
    question: str,
    *,
    repo: Path,
    on_tool_call: Callable[[str, dict[str, Any]], None] | None = None,
    on_hook_denial: Callable[[str, str], None] | None = None,
    on_hook_feedback: Callable[[str, str], None] | None = None,
    on_model_call: Callable[[int], None] | None = None,
    stats: "LoopStats | None" = None,
    history: list[dict[str, Any]] | None = None,
    on_message: Callable[[dict[str, Any]], None] | None = None,
    mode: str = "execute",
    todos: "TodoList | None" = None,
    on_todos: Callable[["TodoList"], None] | None = None,
    permissions: "Permissions | None" = None,
    approver: "Approver | None" = None,
    on_permission: "PermissionEvent | None" = None,
) -> Turn:
    from harness.hooks import HookPipeline, load_project_hooks
    from harness.plan_mode import PLAN_TOOLS, mode_prompt, plan_mode_policy, todo_tool
    from harness.project_memory import load_memory, memory_prompt
    from harness.tool_loop import run_tool_loop
    from harness.tools import build_tools

    if mode not in {"plan", "execute"}:
        raise ValueError(f"unknown mode: {mode}")
    tools, definitions = build_tools(repo)
    if todos is not None:
        tools["write_todos"], definition = todo_tool(todos, on_todos)
        definitions.append(definition)
    hooks = load_project_hooks(repo, on_hook_feedback)
    if mode == "plan":
        # Plan mode: write tools are not offered, and the policy denies them anyway.
        definitions = [item for item in definitions if item["name"] in PLAN_TOOLS]
        hooks = HookPipeline((plan_mode_policy, *hooks.pre_tool), hooks.pre_model, hooks.post_tool)
    if permissions is not None:
        # Last pre_tool check, so nobody is asked about a call a hook would deny.
        hooks = HookPipeline((*hooks.pre_tool, permissions.hook(approver, on_permission)),
                             hooks.pre_model, hooks.post_tool)
    # Memory files are read for every question, so edits apply on the next one.
    sections = (SYSTEM_PROMPT, memory_prompt(load_memory(repo)), mode_prompt(mode, todos))
    system = "\n\n".join(part for part in sections if part)
    return run_tool_loop(
        client,
        question,
        system,
        tools,
        tool_definitions=definitions,
        max_iterations=MAX_ITERATIONS,
        hooks=hooks,
        on_tool_call=on_tool_call,
        on_hook_denial=on_hook_denial,
        on_model_call=on_model_call,
        stats=stats,
        history=history,
        on_message=on_message,
    )
