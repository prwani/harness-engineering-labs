"""Run learner questions with the capabilities available in this snapshot."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from harness.bare import run_bare
from harness.models.adapters import ModelClient, Turn


def ask_with_tools(
    client: ModelClient,
    question: str,
    *,
    repo: Path,
    on_tool_call: Callable[[str, dict[str, Any]], None] | None = None,
    on_hook_denial: Callable[[str, str], None] | None = None,
) -> Turn:
    from harness.tool_loop import run_tool_loop
    from harness.tools import build_tools

    tools, definitions = build_tools(repo)
    return run_tool_loop(
        client,
        question,
        "Answer from evidence. Git and Azure CLI calls are restricted to a few read "
        "commands by pre-tool hooks; shell calls are denied. A denied call is not an "
        "execution. Use the available repository helpers when relevant.",
        tools,
        tool_definitions=definitions,
        max_iterations=8,
        on_tool_call=on_tool_call,
        on_hook_denial=on_hook_denial,
    )
