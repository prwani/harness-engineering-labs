"""Learner-facing model question command."""

import typer

from harness.models.foundry import create_model_client


def register_ask_command(app: typer.Typer, *, tools_enabled: bool = False) -> None:
    if tools_enabled:
        from pathlib import Path

        from harness.learner import ask_with_tools

        @app.command("ask")
        def ask(
            question: str,
            repo: Path | None = typer.Option(None, "--repo", help="Repository root for read-only tools."),
            azure: bool = typer.Option(False, "--azure", help="Allow read-only Azure CLI tools."),
        ) -> None:
            """Ask a question; use read-only repository and optional Azure tools."""
            try:
                turn = ask_with_tools(create_model_client(), question, repo=repo or Path.cwd(), azure=azure)
            except Exception as error:
                typer.echo(f"Unable to answer question: {error}", err=True)
                raise typer.Exit(1) from error
            typer.echo(turn.text)
            typer.echo(f"Tokens: input={turn.usage.input_tokens}, output={turn.usage.output_tokens}")
        return

    @app.command("ask")
    def ask(question: str) -> None:
        """Ask one stateless question without tools or memory."""
        try:
            client = create_model_client()
            system = "Answer directly and accurately. If uncertain, say what is unknown."
            try:
                from harness.bare import run_bare
            except ImportError:
                turn = client.complete(
                    system=system, messages=[{"role": "user", "content": question}], tools=[]
                )
            else:
                turn = run_bare(client, question, system)
        except Exception as error:
            typer.echo(f"Unable to answer question: {error}", err=True)
            raise typer.Exit(1) from error
        typer.echo(turn.text)
        typer.echo(f"Tokens: input={turn.usage.input_tokens}, output={turn.usage.output_tokens}")
