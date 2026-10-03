"""Thin harness CLI."""

import json
from pathlib import Path
import subprocess
import sys
from urllib.error import URLError
from urllib.request import Request, urlopen

import typer

from harness.cli.learner import register_ask_command
from harness.approval import harness_policy
from harness.config import HarnessConfig, foundry_token_provider
from harness.lab_features import load_features
from harness.memory import SessionMemory
from harness.planning import ModeSwitch

app = typer.Typer(no_args_is_help=True)
register_ask_command(app, tools_enabled=True)
sim_app = typer.Typer(no_args_is_help=True)
memory_app = typer.Typer(no_args_is_help=True)
app.add_typer(sim_app, name="sim")
app.add_typer(memory_app, name="memory")


@app.command()
def approvals(tool: str, reason: str = typer.Option("", "--reason")) -> None:
    """Show the policy decision the harness would make for a tool call."""
    decision = harness_policy(tool, {"reason": reason} if reason else {})
    typer.echo(json.dumps({"tool": tool, "decision": decision.decision.value, "reason": decision.reason}))


@memory_app.command("files")
def memory_files(repo: str = typer.Option(".", "--repo", help="Project directory.")) -> None:
    """Show which HARNESS.md memory files `harness ask` loads."""
    from harness.project_memory import describe_memory

    typer.echo(describe_memory(Path(repo).resolve()))


@memory_app.command("ls")
def memory_ls(root: str = "memory") -> None:
    """List files in session memory."""
    memory_root = Path(root)
    names = sorted(p.name for p in memory_root.iterdir()) if memory_root.exists() else []
    typer.echo(json.dumps(names))


@memory_app.command("show")
def memory_show(name: str, root: str = "memory") -> None:
    """Print one session-memory file."""
    typer.echo(SessionMemory(root=Path(root)).read(name))


@app.command()
def mode(target: str = typer.Argument(..., help="plan or execute")) -> None:
    """Switch the active agent spec. Only the harness may do this."""
    switch = ModeSwitch()
    spec = switch.switch(target)
    typer.echo(json.dumps({"mode": switch.mode, "agent": spec.name, "tools": list(spec.tools)}))


@app.command()
def sessions(
    repo: Path | None = typer.Option(None, "--repo", help="Project whose sessions to list."),
) -> None:
    """List this project's saved sessions, most recent first."""
    from harness.session import SessionStore

    store = SessionStore(repo or Path.cwd())
    infos = store.list()
    if not infos:
        typer.echo(f"No sessions in {store.root}")
        return
    typer.echo(f"Sessions in {store.root}")
    for info in infos:
        name = info.name or "-"
        fork = f" (fork of {info.forked_from[:8]})" if info.forked_from else ""
        typer.echo(f"{info.session_id[:8]}  {name:<20} {info.messages:>4} msgs "
                   f"{info.size / 1024:>7.1f} KB  {info.title}{fork}")


@app.command("permissions")
def permissions(
    repo: str = typer.Option(".", "--repo", help="Project directory."),
    accept_edits: bool = typer.Option(False, "--accept-edits", help="Show the --accept-edits defaults."),
) -> None:
    """Show the permission rules `harness ask` applies, and where each came from."""
    from harness.permissions import Permissions

    typer.echo(Permissions.load(Path(repo).resolve(), accept_edits=accept_edits).describe())


@app.command("trace")
def trace_summary(
    path: Path = typer.Argument(..., help="JSONL file written by `harness ask --trace`."),
    input_price: float | None = typer.Option(None, "--input-price", help="USD per 1M input tokens."),
    output_price: float | None = typer.Option(None, "--output-price", help="USD per 1M output tokens."),
) -> None:
    """Summarize a trace: LLM calls, tokens, tools, hooks, permissions, time and cost."""
    from harness.tracing import prices, summarize

    default_in, default_out = prices()
    typer.echo(summarize(path, input_price if input_price is not None else default_in,
                         output_price if output_price is not None else default_out))


mcp_app = typer.Typer(no_args_is_help=True, help="MCP servers for the current project.")
app.add_typer(mcp_app, name="mcp")


@mcp_app.command("add")
def mcp_add(
    name: str,
    command: list[str] = typer.Argument(..., help="Server command, after --."),
    repo: str = typer.Option(".", "--repo", help="Project directory."),
) -> None:
    """Register a stdio MCP server for this project: harness mcp add NAME -- COMMAND..."""
    from harness.mcp_client import add_server, config_path

    root = Path(repo).resolve()
    add_server(root, name, command)
    typer.echo(f"Added MCP server {name} to {config_path(root)}")


@mcp_app.command("list")
def mcp_list(repo: str = typer.Option(".", "--repo", help="Project directory.")) -> None:
    """Start each registered server and list its tools."""
    from harness.mcp_client import describe_servers, start_servers

    root = Path(repo).resolve()
    running = start_servers(root, lambda name, error: typer.echo(f"{name}: failed: {error}", err=True))
    try:
        typer.echo(describe_servers(root, running))
    finally:
        for server in running:
            server.close()


@mcp_app.command("remove")
def mcp_remove(name: str, repo: str = typer.Option(".", "--repo", help="Project directory.")) -> None:
    """Unregister an MCP server from this project."""
    from harness.mcp_client import remove_server

    if not remove_server(Path(repo).resolve(), name):
        typer.echo(f"No MCP server named {name}.", err=True)
        raise typer.Exit(1)
    typer.echo(f"Removed MCP server {name}.")


@app.command("skills")
def skills_list(repo: str = typer.Option(".", "--repo", help="Project directory.")) -> None:
    """List the skills `harness ask` can use in this project."""
    from harness.project_skills import describe_skills, discover_skills

    typer.echo(describe_skills(discover_skills(Path(repo).resolve())))


@app.command("agents")
def background_agents(repo: str = typer.Option(".", "--repo", help="Project directory.")) -> None:
    """List background agents started with `harness ask --bg`."""
    from harness.background import describe

    typer.echo(describe(Path(repo)))


@app.command("logs")
def background_logs(name: str, repo: str = typer.Option(".", "--repo", help="Project directory.")) -> None:
    """Show a background agent's output so far."""
    from harness.background import load

    agent = load(Path(repo).resolve(), name)
    log = Path(agent.log)
    typer.echo(log.read_text(encoding="utf-8") if log.is_file() else "No output yet.")
    typer.echo(f"Status: {agent.status}. Worktree: {agent.worktree}. Trace: {agent.trace}")


@app.command("rm")
def background_rm(
    name: str,
    repo: str = typer.Option(".", "--repo", help="Project directory."),
    force: bool = typer.Option(False, "--force", help="Also discard uncommitted changes in its worktree."),
) -> None:
    """Remove a finished background agent, its worktree and its branch."""
    from harness.background import remove

    try:
        remove(Path(repo), name, force=force)
    except (RuntimeError, ValueError) as error:
        typer.echo(f"Not removed: {error}", err=True)
        raise typer.Exit(1) from error
    typer.echo(f"Removed background agent {name}.")


@app.command("lab-info")
def lab_info() -> None:
    """Show the snapshot's implemented and live-validation scope."""
    features = load_features()
    typer.echo(json.dumps({
        "number": features.number,
        "slug": features.slug,
        "title": features.title,
        "capabilities": features.capabilities,
        "live_validation": features.live_validation,
    }, indent=2))


@app.command()
def whoami() -> None:
    """Confirm an Entra token can be acquired without exposing it."""
    try:
        foundry_token_provider()()
    except Exception as error:
        typer.echo(f"Unable to acquire Foundry Entra token: {error}", err=True)
        raise typer.Exit(1) from error
    typer.echo("Foundry Entra token acquired.")


@app.command()
def ping(provider: str | None = typer.Option(None), probe: bool = False) -> None:
    """Validate configuration and record declared deployment capabilities."""
    config = HarnessConfig.from_env()
    provider = provider or config.provider
    if provider not in {"claude", "gpt"}:
        raise typer.BadParameter("provider must be claude or gpt")
    if not config.endpoint:
        raise typer.BadParameter("FOUNDRY_ENDPOINT is not configured")
    deployment = config.deployment_for(provider)
    result = {"provider": provider, "deployment": deployment}
    if probe:
        result["capabilities"] = {
            "parallel_tool_calls": None,
            "reasoning_items": provider == "gpt",
            "supports_cache_breakpoints": None,
        }
        target = Path("runs/capabilities.json")
        target.parent.mkdir(parents=True, exist_ok=True)
        capabilities = json.loads(target.read_text()) if target.exists() else {}
        capabilities[provider] = result
        target.write_text(json.dumps(capabilities, indent=2))
    typer.echo(json.dumps(result))


@sim_app.command("start")
def sim_start(port: int = 8000) -> None:
    """Start the local simulator in the foreground."""
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "common.store_sim.app:app",
         "--host", "127.0.0.1", "--port", str(port)],
        check=True,
    )


def _sim_request(path: str, method: str = "GET", port: int = 8000) -> str:
    try:
        with urlopen(Request(f"http://127.0.0.1:{port}{path}", method=method), timeout=5) as response:
            return response.read().decode()
    except URLError as error:
        typer.echo(f"Store Simulator is unavailable: {error.reason}", err=True)
        raise typer.Exit(1) from error


@sim_app.command("status")
def sim_status(port: int = 8000) -> None:
    """Print products from the running simulator."""
    typer.echo(json.dumps(json.loads(_sim_request("/product", port=port)), indent=2))


@sim_app.command("reset")
def sim_reset(port: int = 8000) -> None:
    """Restore seed data in the running simulator."""
    _sim_request("/reset", "POST", port)
    typer.echo("Simulator reset.")
