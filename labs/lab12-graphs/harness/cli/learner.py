"""Learner-facing model question command."""

import typer

from harness.cli.interactive import Activity, render_turn, run_interactive
from harness.models.foundry import create_model_client


def describe_session(session) -> str:
    label = f" '{session.name}'" if session.name else ""
    fork = f", fork of {session.forked_from[:8]}" if session.forked_from else ""
    return f"Session {session.session_id[:8]}{label}: {len(session.messages)} messages{fork}"


def activity_events(activity: Activity, root=None):
    """Show tool calls and hook decisions as permanent lines above the spinner."""
    from harness.chat import Events

    def on_model_call(number: int) -> None:
        activity.status(f"waiting for model (LLM call {number})")

    def on_tool_call(name: str, args: dict) -> None:
        activity.echo(f"Tool: {name}({args})")
        activity.status(f"running {name}", announce=False)

    def approver(name: str, args: dict, why: str) -> str:
        from harness.permissions import subject

        target = subject(root, name, args) if root else args
        while True:
            answer = activity.ask(f"Permission: {name}({target}) [{why}]\n"
                                  "Allow? [y]es / [n]o / [a]lways this session: ").strip().lower()
            if answer[:1] in {"y", "n", "a"} or not answer:
                return answer[:1] or "n"

    return Events(
        approver=approver,
        on_tool_call=on_tool_call,
        on_hook_denial=lambda name, reason: activity.echo(f"Hook: denied {name}: {reason}"),
        on_hook_feedback=lambda name, message: activity.echo(f"Hook: {name}: {message}"),
        on_model_call=on_model_call,
    )


def register_ask_command(app: typer.Typer, *, tools_enabled: bool = False) -> None:
    if tools_enabled:
        from pathlib import Path

        from harness.chat import APPROVED, Chat
        from harness.plan_mode import render_todos
        from harness.project_memory import INIT_PROMPT, describe_memory
        from harness.session import SessionStore
        from harness.tool_loop import LoopStats
        from harness.agents import describe_agents
        from harness.mcp_client import describe_servers
        from harness.project_skills import describe_skills
        from harness.tracing import describe_context, describe_cost

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
            plan: bool = typer.Option(
                False, "--plan", help="Start in plan mode: read-only tools, no edits."
            ),
            accept_edits: bool = typer.Option(
                False, "--accept-edits", help="Allow write_file/edit_file without asking (rules still apply)."
            ),
            trace: Path | None = typer.Option(
                None, "--trace", help="Append every step of each run to this JSONL file."
            ),
            compact_at: int | None = typer.Option(
                None, "--compact-at", min=1000,
                help="Compact automatically before a question once a request reaches this many input tokens.",
            ),
            max_iterations: int | None = typer.Option(
                None, "--max-iterations", min=1,
                help="Most model calls per question (default 30), including stop-hook retries.",
            ),
            background: bool = typer.Option(
                False, "--bg", help="Run the question detached in a new worktree; needs -n NAME."
            ),
        ) -> None:
            """Ask a question or open the interactive prompt, in a saved session."""
            try:
                root = repo or Path.cwd()
                if background:
                    from harness import background as bg

                    if not question or not name:
                        raise ValueError("--bg needs -n NAME and a question")
                    agent = bg.start(root, name, question)
                    typer.echo(f"Started background agent {agent.name} (pid {agent.pid}) "
                               f"in {agent.worktree} on branch {agent.branch}.")
                    typer.echo(f"Check on it with: harness agents, harness logs {agent.name}")
                    return
                session = SessionStore(root).open(
                    name=name, continue_latest=continue_latest, resume=resume, fork=fork
                )
                typer.echo(describe_session(session))
                chat = Chat(create_model_client(), root, session,
                            mode="plan" if plan else "execute", accept_edits=accept_edits,
                            trace_path=trace, compact_at=compact_at,
                            max_iterations=max_iterations,
                            on_mcp_error=lambda name, error: typer.echo(
                                f"MCP server {name} failed to start: {error}", err=True))
                if plan:
                    typer.echo("Plan mode: write tools are off. Type /execute to approve the plan.")

                def compact(instructions: str) -> None:
                    with Activity() as activity:
                        activity.status("compacting")
                        before, after, summary = chat.compact(instructions)
                    typer.echo(f"Compacted ~{before} tokens of history into a ~{after}-token summary:")
                    typer.echo(summary)

                def clear(_: str) -> None:
                    chat.clear()
                    typer.echo("Conversation cleared; the session continues with an empty history.")

                def respond(prompt: str) -> None:
                    if chat.needs_compaction():
                        typer.echo(f"Context reached {chat.meter.last_input_tokens} input tokens "
                                   f"(--compact-at {chat.compact_at}); compacting first.")
                        compact("")
                    stats = LoopStats()
                    with Activity() as activity:
                        events = activity_events(activity, root)
                        turn = chat.ask(prompt, events, stats)
                    render_turn(turn, elapsed=activity.elapsed, stats=stats)

                def show_session(_: str) -> None:
                    typer.echo(describe_session(session))
                    typer.echo(f"File: {session.path}")

                def show_history(_: str) -> None:
                    for number, text in enumerate(chat.questions(), 1):
                        typer.echo(f"{number}. {text.splitlines()[0][:100]}")
                    if not chat.questions():
                        typer.echo("No questions yet.")

                def show_todos(_: str) -> None:
                    typer.echo(render_todos(chat.todos))

                def enter_plan_mode(_: str) -> None:
                    chat.set_mode("plan")
                    typer.echo("Plan mode: write tools are off. Type /execute to approve the plan.")

                def execute(extra: str) -> None:
                    chat.set_mode("execute")
                    typer.echo("Execute mode: the plan is approved and write tools are on.")
                    respond(f"{APPROVED} {extra}".strip())

                def show_memory(_: str) -> None:
                    typer.echo(describe_memory(root))

                def init_memory(extra: str) -> None:
                    respond(f"{INIT_PROMPT} {extra}".strip())

                def show_permissions(_: str) -> None:
                    typer.echo(chat.permissions.describe())

                commands = {
                    "/session": show_session, "/history": show_history, "/todos": show_todos,
                    "/plan": enter_plan_mode, "/execute": execute,
                    "/memory": show_memory, "/init": init_memory,
                    "/permissions": show_permissions,
                    "/cost": lambda _: typer.echo(describe_cost(chat.meter)),
                    "/context": lambda _: typer.echo(describe_context(chat.meter, session.messages)),
                    "/compact": compact, "/clear": clear,
                    "/skills": lambda _: typer.echo(describe_skills(chat.skills)),
                    "/mcp": lambda _: typer.echo(describe_servers(root, chat.servers)),
                    "/agents": lambda _: typer.echo(describe_agents(chat.agents)),
                }
                for skill_name in chat.skills:
                    # /<skill-name> [extra] loads the skill directly; built-ins win.
                    commands.setdefault(
                        f"/{skill_name}",
                        lambda extra, skill_name=skill_name: respond(chat.skill_prompt(skill_name, extra)),
                    )
                try:
                    if question is None:
                        run_interactive(
                            respond, commands,
                            prompt=lambda: "You [plan]> " if chat.mode == "plan" else "You> ",
                        )
                    elif question.startswith("/") and question.split()[0] in commands:
                        name, _, rest = question.partition(" ")
                        commands[name](rest.strip())
                    else:
                        respond(question)
                finally:
                    chat.close()
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
