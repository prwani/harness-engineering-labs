"""Learner-facing model question command."""

import typer

from harness.cli.interactive import Activity, render_turn, run_interactive
from harness.models.foundry import create_model_client


def describe_session(session) -> str:
    label = f" '{session.name}'" if session.name else ""
    fork = f", fork of {session.forked_from[:8]}" if session.forked_from else ""
    return f"Session {session.session_id[:8]}{label}: {len(session.messages)} messages{fork}"


def register_ask_command(app: typer.Typer, *, tools_enabled: bool = False) -> None:
    if tools_enabled:
        from pathlib import Path

        from harness.learner import ask_with_tools
        from harness.session import SessionStore
        from harness.tool_loop import LoopStats

        @app.command("ask")
        def ask(
            question: str | None = typer.Argument(
                None, help="Question to ask; omit to open the interactive prompt."
            ),
            repo: Path | None = typer.Option(
                None, "--repo", help="Working directory for repository and CLI tools."
            ),
            name: str | None = typer.Option(None, "--name", "-n", help="Name for a new session."),
            continue_latest: bool = typer.Option(
                False, "--continue", "-c", help="Continue the most recent session in this project."
            ),
            resume: str | None = typer.Option(
                None, "--resume", "-r", help="Resume a session by ID, ID prefix or name."
            ),
            fork: bool = typer.Option(
                False, "--fork", help="With -c or -r: continue in a new copy of the session."
            ),
        ) -> None:
            """Ask a question or open the interactive prompt, in a saved session."""
            try:
                root = repo or Path.cwd()
                session = SessionStore(root).open(
                    name=name, continue_latest=continue_latest, resume=resume, fork=fork
                )
                typer.echo(describe_session(session))
                client = create_model_client()

                def respond(prompt: str) -> None:
                    stats = LoopStats()
                    with Activity() as activity:

                        def on_model_call(number: int) -> None:
                            activity.status(f"waiting for model (LLM call {number})")

                        def on_tool_call(name: str, args: dict) -> None:
                            activity.echo(f"Tool: {name}({args})")
                            activity.status(f"running {name}", announce=False)

                        def on_hook_denial(name: str, reason: str) -> None:
                            activity.echo(f"Hook: denied {name}: {reason}")

                        def on_hook_feedback(name: str, message: str) -> None:
                            activity.echo(f"Hook: {name}: {message}")

                        turn = ask_with_tools(
                            client,
                            prompt,
                            repo=root,
                            on_tool_call=on_tool_call,
                            on_hook_denial=on_hook_denial,
                            on_hook_feedback=on_hook_feedback,
                            on_model_call=on_model_call,
                            stats=stats,
                            history=session.messages,
                            on_message=session.save,
                        )
                    render_turn(turn, elapsed=activity.elapsed, stats=stats)

                def show_session(_: str) -> None:
                    typer.echo(describe_session(session))
                    typer.echo(f"File: {session.path}")

                def show_history(_: str) -> None:
                    questions = [message["content"] for message in session.messages
                                 if message["role"] == "user" and isinstance(message["content"], str)]
                    for number, text in enumerate(questions, 1):
                        typer.echo(f"{number}. {text.splitlines()[0][:100]}")
                    if not questions:
                        typer.echo("No questions yet.")

                if question is None:
                    run_interactive(respond, {"/session": show_session, "/history": show_history})
                else:
                    respond(question)
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

            def respond(prompt: str) -> None:
                with Activity() as activity:
                    activity.status("waiting for model")
                    turn = answer(prompt)
                render_turn(turn, elapsed=activity.elapsed)

            if question is None:
                run_interactive(respond)
            else:
                respond(question)
        except Exception as error:
            typer.echo(f"Unable to answer question: {error}", err=True)
            raise typer.Exit(1) from error
