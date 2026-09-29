"""Terminal prompt loop for learner-facing questions."""

from collections.abc import Callable

import typer

from harness.models import Turn


def render_turn(turn: Turn) -> None:
    typer.echo(f"Assistant>\n{turn.text}")
    typer.echo(f"Tokens: input={turn.usage.input_tokens}, output={turn.usage.output_tokens}")


def run_interactive(answer: Callable[[str], Turn]) -> None:
    typer.echo("Interactive harness. Type /exit or /quit to leave.")
    while True:
        try:
            question = input("You> ").strip()
        except EOFError:
            typer.echo("")
            return
        if question.lower() in {"/exit", "/quit"}:
            return
        if not question:
            continue
        try:
            render_turn(answer(question))
        except Exception as error:
            typer.echo(f"Unable to answer question: {error}", err=True)
