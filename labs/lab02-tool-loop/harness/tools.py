"""Read-only local repository, Git, and opt-in Azure CLI tools."""

import json
from pathlib import Path
import subprocess
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


def _safe_path(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("Requested path is outside the selected repository.")
    return candidate


def build_read_only_tools(
    repository: Path, *, azure: bool = False
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    root = repository.resolve()
    if not root.is_dir():
        raise ValueError(f"Repository directory does not exist: {root}")

    def list_files(args: dict[str, Any]) -> str:
        directory = _safe_path(root, str(args.get("path", ".")))
        if not directory.is_dir():
            raise ValueError("Requested path is not a directory.")
        ignored = {".git", ".venv", "node_modules", "__pycache__"}
        results = []
        for path in sorted(directory.rglob("*")):
            if any(part in ignored for part in path.relative_to(root).parts):
                continue
            if path.is_file():
                results.append(path.relative_to(root).as_posix())
            if len(results) == 100:
                break
        return "\n".join(results) or "(no files found)"

    def read_file(args: dict[str, Any]) -> str:
        path = _safe_path(root, str(args["path"]))
        if not path.is_file():
            raise ValueError("Requested path is not a regular file.")
        if path.stat().st_size > 100_000:
            raise ValueError("File exceeds the 100 KB read limit.")
        return path.read_text(encoding="utf-8")[:20_000]

    def git_status(_: dict[str, Any]) -> str:
        return _run(["git", "status", "--short", "--branch"], cwd=root)

    def git_log(args: dict[str, Any]) -> str:
        limit = max(1, min(int(args.get("limit", 5)), 20))
        return _run(["git", "log", f"-{limit}", "--oneline", "--decorate"], cwd=root)

    tools: dict[str, Any] = {
        "list_files": list_files,
        "read_file": read_file,
        "git_status": git_status,
        "git_log": git_log,
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
            "description": "Read a UTF-8 text file up to 100 KB under the repository root.",
            "input_schema": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Repository-relative file path"}},
                "required": ["path"],
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
    ]

    if azure:
        def azure_account(_: dict[str, Any]) -> str:
            return _run(
                ["az", "account", "show", "--query", "{name:name,tenantId:tenantId}", "--output", "json"],
                cwd=root,
            )

        def azure_resources(_: dict[str, Any]) -> str:
            result = _run(
                ["az", "resource", "list", "--query", "[0:20].{name:name,type:type,location:location}", "--output", "json"],
                cwd=root,
                timeout=30,
            )
            resources = json.loads(result)
            return json.dumps(resources, indent=2)

        tools.update({"azure_account": azure_account, "azure_resources": azure_resources})
        definitions.extend([
            {
                "name": "azure_account",
                "description": "Show the active Azure CLI account name and tenant ID.",
                "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
            },
            {
                "name": "azure_resources",
                "description": "List up to 20 Azure resources visible to the signed-in Azure CLI account.",
                "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
            },
        ])
    return tools, definitions
