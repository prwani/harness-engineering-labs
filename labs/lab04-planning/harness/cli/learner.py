"""Learner-facing model question command."""

import typer

from harness.cli.interactive import render_turn, run_interactive
from harness.models.foundry import create_model_client


def register_ask_command(app: typer.Typer) -> None:
    @app.command("ask")
    def ask(
        question: str | None = typer.Argument(
            None, help="Question to ask; omit to open the interactive prompt."
        ),
    ) -> None:
        """Ask a question or open the interactive prompt."""
        try:
            client = create_model_client()
            system = (
                "Answer the user's question directly and accurately. "
                "If uncertain, say what is unknown."
            )

            def answer(prompt: str):
                from harness.bare import run_bare

                return run_bare(client, prompt, system)

            if question is None:
                run_interactive(answer)
            else:
                render_turn(answer(question))
        except Exception as error:
            typer.echo(f"Unable to answer question: {error}", err=True)
            raise typer.Exit(1) from error
