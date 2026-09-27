"""Thin Lab 0 CLI."""

import json
from pathlib import Path
import subprocess
import sys
from urllib.error import URLError
from urllib.request import Request, urlopen

import typer

from harness.config import HarnessConfig, foundry_token_provider

app = typer.Typer(no_args_is_help=True)
sim_app = typer.Typer(no_args_is_help=True)
app.add_typer(sim_app, name="sim")


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


def _sim_request(path: str, method: str = "GET") -> str:
    try:
        with urlopen(Request(f"http://127.0.0.1:8000{path}", method=method), timeout=5) as response:
            return response.read().decode()
    except URLError as error:
        typer.echo(f"Store Simulator is unavailable: {error.reason}", err=True)
        raise typer.Exit(1) from error


@sim_app.command("status")
def sim_status() -> None:
    """Print products from the running simulator."""
    typer.echo(json.dumps(json.loads(_sim_request("/product")), indent=2))


@sim_app.command("reset")
def sim_reset() -> None:
    """Restore seed data in the running simulator."""
    _sim_request("/reset", "POST")
    typer.echo("Simulator reset.")
