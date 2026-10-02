"""A minimal MCP client over stdio, and the per-project server registry.

An MCP server is a separate process that offers tools. The harness starts
it, speaks JSON-RPC 2.0 over its stdin/stdout (``initialize``,
``tools/list``, ``tools/call``) and exposes each tool to the model as
``mcp__<server>__<tool>``, so it can never collide with a local tool.
Everything else is unchanged: MCP calls go through the same hooks,
permissions (unknown tools ask by default) and trace as local tools.

``harness mcp add NAME -- COMMAND...`` stores servers for the current
project in ``$HARNESS_HOME/projects/<project>/mcp.json``, outside the
repository, like Claude Code's local scope.
"""

from dataclasses import dataclass, field
import json
from pathlib import Path
import queue
import re
import subprocess
import sys
import threading
from typing import Any

from harness.session import project_dir

PROTOCOL_VERSION = "2024-11-05"
TIMEOUT_SECONDS = 30
_NAME = r"^[A-Za-z0-9_-]+$"


def config_path(repo: Path) -> Path:
    return project_dir(repo) / "mcp.json"


def load_servers(repo: Path) -> dict[str, list[str]]:
    path = config_path(repo)
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def save_servers(repo: Path, servers: dict[str, list[str]]) -> None:
    path = config_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(servers, indent=2), encoding="utf-8")


def add_server(repo: Path, name: str, command: list[str]) -> None:
    if not re.match(_NAME, name) or "__" in name:
        raise ValueError("server name must be letters, digits, '-' or '_' (no '__')")
    if not command:
        raise ValueError("give the server command after --")
    servers = load_servers(repo)
    servers[name] = command
    save_servers(repo, servers)


def remove_server(repo: Path, name: str) -> bool:
    servers = load_servers(repo)
    if servers.pop(name, None) is None:
        return False
    save_servers(repo, servers)
    return True


@dataclass
class MCPServer:
    """One running stdio server."""

    name: str
    command: list[str]
    cwd: Path
    tools: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        command = list(self.command)
        if command[0] in {"python", "python3"}:
            command[0] = sys.executable
        self._process = subprocess.Popen(
            command, cwd=self.cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, encoding="utf-8", bufsize=1,
        )
        self._lines: queue.Queue[str | None] = queue.Queue()
        threading.Thread(target=self._read, daemon=True).start()
        self._next_id = 0
        try:
            self._request("initialize", {
                "protocolVersion": PROTOCOL_VERSION, "capabilities": {},
                "clientInfo": {"name": "harness", "version": "0.1.0"},
            })
            self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})
            self.tools = self._request("tools/list", {}).get("tools", [])
        except Exception:
            self.close()
            raise

    def _read(self) -> None:
        for line in self._process.stdout:
            self._lines.put(line)
        self._lines.put(None)

    def _send(self, message: dict[str, Any]) -> None:
        self._process.stdin.write(json.dumps(message) + "\n")
        self._process.stdin.flush()

    def _request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        self._next_id += 1
        self._send({"jsonrpc": "2.0", "id": self._next_id, "method": method, "params": params})
        while True:
            try:
                line = self._lines.get(timeout=TIMEOUT_SECONDS)
            except queue.Empty:
                raise TimeoutError(f"MCP server {self.name} did not answer {method}") from None
            if line is None:
                raise RuntimeError(f"MCP server {self.name} exited")
            if not line.strip():
                continue
            message = json.loads(line)
            if message.get("id") != self._next_id:
                continue  # a notification or a stale reply
            if "error" in message:
                raise RuntimeError(f"MCP {method} failed: {message['error'].get('message')}")
            return message.get("result") or {}

    def call(self, tool: str, args: dict[str, Any]) -> str:
        result = self._request("tools/call", {"name": tool, "arguments": args})
        text = "\n".join(item.get("text", "") for item in result.get("content", []) if item.get("type") == "text")
        if result.get("isError"):
            raise RuntimeError(text or f"{tool} failed")
        return text

    def close(self) -> None:
        if self._process.poll() is None:
            self._process.stdin.close()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()


def tool_name(server: str, tool: str) -> str:
    return f"mcp__{server}__{tool}"


def mcp_tools(servers: list[MCPServer]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Harness tools and model definitions for every tool of every server."""
    tools: dict[str, Any] = {}
    definitions = []
    for server in servers:
        for spec in server.tools:
            name = tool_name(server.name, spec["name"])
            tools[name] = lambda args, server=server, tool=spec["name"]: server.call(tool, args)
            definitions.append({
                "name": name,
                "description": f"[MCP server {server.name}] {spec.get('description', '')}".strip(),
                "input_schema": spec.get("inputSchema") or {"type": "object", "properties": {}},
            })
    return tools, definitions


def start_servers(repo: Path, on_error=None) -> list[MCPServer]:
    """Start every registered server; one that fails is reported and skipped."""
    running = []
    for name, command in load_servers(repo).items():
        try:
            running.append(MCPServer(name, command, repo))
        except Exception as error:
            if on_error:
                on_error(name, error)
    return running


def describe_servers(repo: Path, running: list[MCPServer] | None = None) -> str:
    servers = load_servers(repo)
    if not servers:
        return "No MCP servers for this project. Add one with: harness mcp add NAME -- COMMAND"
    by_name = {server.name: server for server in running or []}
    lines = []
    for name, command in servers.items():
        server = by_name.get(name)
        status = (", ".join(tool_name(name, spec["name"]) for spec in server.tools) or "no tools") \
            if server else "not running"
        lines.append(f"{name}: {' '.join(command)}\n    {status}")
    return "\n".join(lines)
