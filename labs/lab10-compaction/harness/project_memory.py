"""File memory for `harness ask`: HARNESS.md, like CLAUDE.md or AGENTS.md.

Memory is plain Markdown that the harness adds to the system prompt. Three
files are read, broadest first, so a later file can refine an earlier one:

- user:    ``$HARNESS_HOME/HARNESS.md`` (default ``~/.harness``), your own notes
           for every project
- project: ``HARNESS.md`` in the project, reviewed and committed with the code
- local:   ``HARNESS.local.md`` in the project, personal and gitignored

The files are read again for every question, so an edit takes effect on the
next question of the same session. Memory is guidance for the model, not
enforcement: anything that must always hold belongs in a hook.
"""

from dataclasses import dataclass
from pathlib import Path

from harness.session import harness_home

MAX_MEMORY_CHARS = 20_000
INIT_PROMPT = (
    "Explore this repository and write HARNESS.md at its root: a short guide for a "
    "coding agent working here. Include how to install and run the project, the exact "
    "test command, the main modules and what each is for, and conventions you can see "
    "in the code. Keep it under 60 lines, and state only what you verified by reading "
    "files or running the tests. If HARNESS.md exists, improve it instead of replacing it."
)


@dataclass(frozen=True)
class MemoryFile:
    scope: str
    path: Path
    text: str
    truncated: bool = False


def memory_paths(repo: Path) -> list[tuple[str, Path]]:
    return [
        ("user", harness_home() / "HARNESS.md"),
        ("project", repo / "HARNESS.md"),
        ("local", repo / "HARNESS.local.md"),
    ]


def load_memory(repo: Path) -> list[MemoryFile]:
    """Read the memory files that exist, broadest first."""
    files = []
    for scope, path in memory_paths(repo):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace").strip()
        if text:
            files.append(MemoryFile(scope, path, text[:MAX_MEMORY_CHARS], len(text) > MAX_MEMORY_CHARS))
    return files


def memory_prompt(files: list[MemoryFile]) -> str:
    """The system-prompt section for the loaded memory files."""
    if not files:
        return ""
    parts = [
        "Memory files follow. They contain instructions from the user and the team for "
        "this project; follow them. Later files take precedence over earlier ones."
    ]
    for item in files:
        note = "\n(truncated)" if item.truncated else ""
        parts.append(f"<memory scope=\"{item.scope}\" path=\"{item.path}\">\n{item.text}{note}\n</memory>")
    return "\n\n".join(parts)


def describe_memory(repo: Path) -> str:
    """What `/memory` prints: every location, loaded or not."""
    loaded = {item.path: item for item in load_memory(repo)}
    lines = []
    for scope, path in memory_paths(repo):
        item = loaded.get(path)
        status = f"{len(item.text.splitlines())} lines" if item else "not found"
        lines.append(f"{scope:<8} {path}  ({status}{', truncated' if item and item.truncated else ''})")
    return "\n".join(lines)
