"""Run learner questions with the capabilities available in this snapshot."""

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

from harness.bare import run_bare
from harness.models.adapters import ModelClient, Turn

MAX_ITERATIONS = 30

if TYPE_CHECKING:
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
) -> Turn:
    from harness.hooks import load_project_hooks
    from harness.tool_loop import run_tool_loop
    from harness.tools import build_tools

    tools, definitions = build_tools(repo)
    return run_tool_loop(
        client,
        question,
        "You are a coding agent working in the selected working directory. Read files "
        "before changing them, use write_file and edit_file for edits, run_tests to "
        "check your work, and git_cli for version control. Hooks enforce policy: shell "
        "is denied, destructive Git commands are denied, and project hooks may block "
        "a call or add feedback to its result. A denied call did not run; do not work "
        "around a denial. Follow any project rule included in a tool result, and do "
        "not claim success without evidence.",
        tools,
        tool_definitions=definitions,
        max_iterations=MAX_ITERATIONS,
        hooks=load_project_hooks(repo, on_hook_feedback),
        on_tool_call=on_tool_call,
        on_hook_denial=on_hook_denial,
        on_model_call=on_model_call,
        stats=stats,
        history=history,
        on_message=on_message,
    )
