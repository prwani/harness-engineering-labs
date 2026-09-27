"""Thin Lab 0 CLI."""

import json
from pathlib import Path
import subprocess
import sys

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
        target.parent.mkdir(exist_ok=True)
        target.write_text(json.dumps({provider: result}, indent=2))
    typer.echo(json.dumps(result))


@sim_app.command("start")
def sim_start(port: int = 8000) -> None:
    """Start the local simulator in the foreground."""
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "common.store_sim.app:app",
         "--host", "127.0.0.1", "--port", str(port)],
        check=True,
    )


@sim_app.command("status")
def sim_status() -> None:
    """Print the deterministic seeded products."""
    from common.store_sim.app import products
    typer.echo(json.dumps(products, indent=2))


@sim_app.command("reset")
def sim_reset() -> None:
    """Restore simulator seed data."""
    from common.store_sim.app import reset
    reset()
    typer.echo("Simulator reset.")
