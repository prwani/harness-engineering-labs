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
    azure: bool = False,
    on_tool_call: Callable[[str, dict[str, Any]], None] | None = None,
) -> Turn:
    from harness.tool_loop import run_tool_loop
    from harness.tools import build_read_only_tools

    tools, definitions = build_read_only_tools(repo, azure=azure)
    return run_tool_loop(
        client,
        question,
        "Answer from evidence. Use repository and Git tools for questions about "
        "the selected repository. Use Azure tools only when relevant. These tools "
        "are read-only; never claim to have changed anything. If evidence is missing, "
        "say so.",
        tools,
        tool_definitions=definitions,
        max_iterations=8,
        on_tool_call=on_tool_call,
    )
