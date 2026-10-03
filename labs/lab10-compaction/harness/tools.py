"""Local repository helpers, file edits, tests, and intentionally unrestricted CLI tools."""

from pathlib import Path
import subprocess
import sys
from typing import Any


def _run(command: list[str], *, cwd: Path, timeout: int = 15) -> str:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as error:
        raise RuntimeError(f"Required command not found: {command[0]}") from error
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(f"Command timed out: {command[0]}") from error
    if result.returncode:
        detail = result.stderr.strip() or f"exit status {result.returncode}"
        raise RuntimeError(f"{command[0]} failed: {detail[:1000]}")
    return result.stdout[:20_000]


def _run_shell(command: str, *, cwd: Path, timeout: int = 30) -> str:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("Shell command timed out.") from error
    if result.returncode:
        detail = result.stderr.strip() or f"exit status {result.returncode}"
        raise RuntimeError(f"Shell command failed: {detail[:1000]}")
    return result.stdout[:20_000]


def _safe_path(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("Requested path is outside the selected repository.")
    return candidate


READ_MAX_LINES = 1000


def _read_lines(path: Path, args: dict[str, Any]) -> str:
    """A range of lines, for files too large to read at once (up to 10 MB)."""
    if path.stat().st_size > 10_000_000:
        raise ValueError("File exceeds the 10 MB read limit.")
    start = int(args.get("start_line", 1))
    count = min(int(args.get("max_lines", READ_MAX_LINES)), READ_MAX_LINES)
    if start < 1 or count < 1:
        raise ValueError("start_line and max_lines must be at least 1.")
    lines = path.read_text(encoding="utf-8").splitlines()
    chunk = lines[start - 1:start - 1 + count]
    end = start + len(chunk) - 1
    return f"[lines {start}-{end} of {len(lines)}]\n" + "\n".join(chunk)


def build_tools(repository: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    root = repository.resolve()
    if not root.is_dir():
        raise ValueError(f"Repository directory does not exist: {root}")

    def list_files(args: dict[str, Any]) -> str:
        directory = _safe_path(root, str(args.get("path", ".")))
        if not directory.is_dir():
            raise ValueError("Requested path is not a directory.")
        ignored = {".git", ".venv", "node_modules", "__pycache__"}
        if any(part in ignored for part in directory.relative_to(root).parts):
            return "(no files found)"

        def walk(current: Path):
            # Prune ignored directories instead of enumerating then filtering them;
            # a local .venv alone can contain tens of thousands of files.
            try:
                entries = sorted(current.iterdir())
            except OSError:
                return
            for path in entries:
                if path.name in ignored or (path.is_symlink() and path.is_dir()):
                    continue
                if path.is_dir():
                    yield from walk(path)
                elif path.is_file():
                    yield path

        results = []
        for path in walk(directory):
            results.append(path.relative_to(root).as_posix())
            if len(results) == 100:
                break
        return "\n".join(results) or "(no files found)"

    def read_file(args: dict[str, Any]) -> str:
        path = _safe_path(root, str(args["path"]))
        if not path.is_file():
            raise ValueError("Requested path is not a regular file.")
        if "start_line" in args or "max_lines" in args:
            return _read_lines(path, args)
        if path.stat().st_size > 100_000:
            raise ValueError("File exceeds the 100 KB read limit; read it in parts with "
                             "start_line and max_lines.")
        text = path.read_text(encoding="utf-8")
        if len(text) <= 20_000:
            return text
        return (text[:20_000] + f"\n[truncated at 20,000 of {len(text):,} characters; "
                "read the rest with start_line and max_lines]")

    def write_file(args: dict[str, Any]) -> str:
        path = _safe_path(root, str(args["path"]))
        if path == root or path.is_dir():
            raise ValueError("Requested path is a directory.")
        content = str(args["content"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return f"Wrote {len(content)} characters to {path.relative_to(root).as_posix()}."

    def edit_file(args: dict[str, Any]) -> str:
        path = _safe_path(root, str(args["path"]))
        if not path.is_file():
            raise ValueError("Requested path is not a regular file.")
        old, new = str(args["old_text"]), str(args["new_text"])
        text = path.read_text(encoding="utf-8")
        count = text.count(old) if old else 0
        if count != 1:
            raise ValueError(f"old_text must match exactly once; it matched {count} times.")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        return f"Edited {path.relative_to(root).as_posix()}."

    def run_tests(args: dict[str, Any]) -> str:
        command = [sys.executable, "-m", "pytest", "-q"]
        if args.get("path"):
            command.append(_safe_path(root, str(args["path"])).relative_to(root).as_posix())
        try:
            result = subprocess.run(
                command, cwd=root, check=False, capture_output=True, text=True, timeout=120,
            )
        except subprocess.TimeoutExpired as error:
            raise RuntimeError("Tests timed out after 120 seconds.") from error
        output = (result.stdout + result.stderr).strip()
        return f"exit_code={result.returncode}\n{output[-8_000:]}"

    def git_status(_: dict[str, Any]) -> str:
        return _run(["git", "status", "--short", "--branch"], cwd=root)

    def git_log(args: dict[str, Any]) -> str:
        limit = max(1, min(int(args.get("limit", 5)), 20))
        return _run(["git", "log", f"-{limit}", "--oneline", "--decorate"], cwd=root)

    def git_cli(args: dict[str, Any]) -> str:
        return _run(["git", *[str(value) for value in args["args"]]], cwd=root, timeout=30)

    def azure_cli(args: dict[str, Any]) -> str:
        return _run(["az", *[str(value) for value in args["args"]]], cwd=root, timeout=60)

    def shell(args: dict[str, Any]) -> str:
        return _run_shell(str(args["command"]), cwd=root)

    tools: dict[str, Any] = {
        "list_files": list_files,
        "read_file": read_file,
        "write_file": write_file,
        "edit_file": edit_file,
        "run_tests": run_tests,
        "git_status": git_status,
        "git_log": git_log,
        "git_cli": git_cli,
        "azure_cli": azure_cli,
        "shell": shell,
    }
    definitions = [
        {
            "name": "list_files",
            "description": "List up to 100 files under a repository-relative directory.",
            "input_schema": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Directory, default ."}},
                "additionalProperties": False,
            },
        },
        {
            "name": "read_file",
            "description": (
                "Read a UTF-8 text file under the repository root: the whole file up to 100 KB, "
                "or a range of up to 1000 lines with start_line and max_lines."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Repository-relative file path"},
                    "start_line": {"type": "integer", "description": "First line to read, from 1"},
                    "max_lines": {"type": "integer", "description": "Number of lines, at most 1000"},
                },
                "required": ["path"],
                "additionalProperties": False,
            },
        },
        {
            "name": "write_file",
            "description": "Create or overwrite a UTF-8 text file under the repository root.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Repository-relative file path"},
                    "content": {"type": "string", "description": "Complete new file content"},
                },
                "required": ["path", "content"],
                "additionalProperties": False,
            },
        },
        {
            "name": "edit_file",
            "description": "Replace one exact, unique occurrence of old_text with new_text in a file.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Repository-relative file path"},
                    "old_text": {"type": "string", "description": "Exact text that appears once"},
                    "new_text": {"type": "string", "description": "Replacement text"},
                },
                "required": ["path", "old_text", "new_text"],
                "additionalProperties": False,
            },
        },
        {
            "name": "run_tests",
            "description": "Run pytest -q in the repository; returns the exit code and output.",
            "input_schema": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Optional test file or directory"}},
                "additionalProperties": False,
            },
        },
        {
            "name": "git_status",
            "description": "Show the current Git branch and short working-tree status.",
            "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        {
            "name": "git_log",
            "description": "Show recent one-line Git commits, up to 20.",
            "input_schema": {
                "type": "object",
                "properties": {"limit": {"type": "integer", "minimum": 1, "maximum": 20}},
                "additionalProperties": False,
            },
        },
        {
            "name": "git_cli",
            "description": "Run Git with arbitrary arguments in the selected working directory.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Arguments passed directly to the git executable.",
                    }
                },
                "required": ["args"],
                "additionalProperties": False,
            },
        },
        {
            "name": "azure_cli",
            "description": "Run Azure CLI with arbitrary arguments in the selected working directory.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "args": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Arguments passed directly to the az executable.",
                    }
                },
                "required": ["args"],
                "additionalProperties": False,
            },
        },
        {
            "name": "shell",
            "description": "Run an arbitrary command through the operating-system shell.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Complete shell command to execute.",
                    }
                },
                "required": ["command"],
                "additionalProperties": False,
            },
        },
    ]
    return tools, definitions
