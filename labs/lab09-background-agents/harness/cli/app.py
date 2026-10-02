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
