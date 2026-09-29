"""Run learner questions with the capabilities available in this snapshot."""

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

from harness.bare import run_bare
from harness.models.adapters import ModelClient, Turn

if TYPE_CHECKING:
    from harness.tool_loop import LoopStats


def ask_with_tools(
    client: ModelClient,
    question: str,
    *,
    repo: Path,
    on_tool_call: Callable[[str, dict[str, Any]], None] | None = None,
    on_model_call: Callable[[int], None] | None = None,
    stats: "LoopStats | None" = None,
) -> Turn:
    from harness.tool_loop import run_tool_loop
    from harness.tools import build_tools

    tools, definitions = build_tools(repo)
    return run_tool_loop(
        client,
        question,
        "Answer from evidence. You have unrestricted Git CLI, Azure CLI, and shell "
        "tools in the selected working directory. Use tools only when relevant, report "
        "commands that change state, and do not claim success without evidence.",
        tools,
        tool_definitions=definitions,
        max_iterations=8,
        on_tool_call=on_tool_call,
        on_model_call=on_model_call,
        stats=stats,
    )
