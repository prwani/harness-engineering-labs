"""Learner-facing model question command."""

import typer

from harness.cli.interactive import render_turn, run_interactive
from harness.models.foundry import create_model_client


def register_ask_command(app: typer.Typer, *, tools_enabled: bool = False) -> None:
    if tools_enabled:
        from pathlib import Path

        from harness.learner import ask_with_tools

        @app.command("ask")
        def ask(
            question: str | None = typer.Argument(
                None, help="Question to ask; omit to open the interactive prompt."
            ),
            repo: Path | None = typer.Option(
                None, "--repo", help="Working directory for repository and CLI tools."
            ),
        ) -> None:
            """Ask a question or open the interactive prompt."""
            try:
                client = create_model_client()

                def answer(prompt: str):
                    return ask_with_tools(
                        client,
                        prompt,
                        repo=repo or Path.cwd(),
                        on_tool_call=lambda name, args: typer.echo(
                            f"Tool: {name}({args})", err=True
                        ),
                        on_hook_denial=lambda name, reason: typer.echo(
                            f"Hook: denied {name}: {reason}", err=True
                        ),
                    )

                if question is None:
                    run_interactive(answer)
                else:
                    render_turn(answer(question))
            except Exception as error:
                typer.echo(f"Unable to answer question: {error}", err=True)
                raise typer.Exit(1) from error
        return

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
            try:
                from harness.bare import run_bare
            except ImportError:
                answer = lambda prompt: client.complete(
                    system=system,
                    messages=[{"role": "user", "content": prompt}],
                    tools=[],
                )
            else:
                answer = lambda prompt: run_bare(client, prompt, system)

            if question is None:
                run_interactive(answer)
            else:
                render_turn(answer(question))
        except Exception as error:
            typer.echo(f"Unable to answer question: {error}", err=True)
            raise typer.Exit(1) from error
