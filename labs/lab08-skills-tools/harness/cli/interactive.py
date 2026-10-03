"""Terminal prompt loop and progress display for learner-facing questions."""

from collections.abc import Callable
import sys
import threading
from time import perf_counter
from typing import TYPE_CHECKING, TextIO

import typer

from harness.models import Turn

if TYPE_CHECKING:
    from harness.tool_loop import LoopStats


class Activity:
    """Show that the harness is working while one question is answered.

    On an interactive terminal, a spinner with the elapsed time is redrawn on
    stderr. Otherwise each announced status is printed once, so redirected
    output and logs stay readable.
    """

    _FRAMES = "|/-\\"

    def __init__(self, stream: TextIO | None = None, interval: float = 0.1) -> None:
        self._stream = stream or sys.stderr
        self._interval = interval
        self._live = self._stream.isatty()
        self._lock = threading.Lock()
        self._stopped = threading.Event()
        self._thread: threading.Thread | None = None
        self._label = ""
        self._width = 0
        self._started = perf_counter()
        self._finished: float | None = None

    def __enter__(self) -> "Activity":
        self._started = perf_counter()
        if self._live:
            self._thread = threading.Thread(target=self._spin, daemon=True)
            self._thread.start()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @property
    def elapsed(self) -> float:
        end = perf_counter() if self._finished is None else self._finished
        return end - self._started

    def status(self, label: str, *, announce: bool = True) -> None:
        """Set the spinner label; print it once when no spinner is shown."""
        with self._lock:
            self._label = label
            if not self._live and announce:
                self._write_line(f"... {label}")

    def echo(self, message: str) -> None:
        """Print a permanent event line without corrupting the spinner."""
        with self._lock:
            self._clear()
            self._write_line(message)

    def ask(self, prompt: str) -> str:
        """Pause the spinner and read one line from the user; EOF reads as ''."""
        with self._lock:
            self._clear()
            try:
                return input(prompt)
            except EOFError:
                typer.echo("")
                return ""

    def close(self) -> None:
        if self._finished is None:
            self._finished = perf_counter()
        self._stopped.set()
        if self._thread:
            self._thread.join()
        with self._lock:
            self._clear()

    def _spin(self) -> None:
        frame = 0
        while not self._stopped.wait(self._interval):
            with self._lock:
                if not self._label:
                    continue
                text = f"{self._FRAMES[frame % len(self._FRAMES)]} {self._label} ({self.elapsed:.1f}s)"
                self._stream.write("\r" + text.ljust(self._width))
                self._stream.flush()
                self._width = len(text)
            frame += 1

    def _clear(self) -> None:
        if self._width:
            self._stream.write("\r" + " " * self._width + "\r")
            self._stream.flush()
            self._width = 0

    def _write_line(self, message: str) -> None:
        self._stream.write(message + "\n")
        self._stream.flush()


def format_summary(stats: "LoopStats") -> str:
    return (
        f"Summary: llm_calls={stats.model_calls}, tool_calls={stats.tool_calls}, "
        f"denied={stats.denied_calls}, tool_errors={stats.tool_errors}, "
        f"model_time={stats.model_seconds:.1f}s, tool_time={stats.tool_seconds:.1f}s"
    )


def render_turn(
    turn: Turn, *, elapsed: float | None = None, stats: "LoopStats | None" = None
) -> None:
    typer.echo(f"Assistant>\n{turn.text}")
    tokens = f"Tokens: input={turn.usage.input_tokens}, output={turn.usage.output_tokens}"
    if elapsed is not None:
        tokens += f" | Time: {elapsed:.1f}s"
    typer.echo(tokens)
    if stats is not None:
        typer.echo(format_summary(stats))


Command = Callable[[str], None]


def run_interactive(
    respond: Callable[[str], None],
    commands: dict[str, Command] | None = None,
    prompt: Callable[[], str] | None = None,
) -> None:
    """Prompt repeatedly; `respond` answers and renders one question.

    `commands` maps slash commands such as ``/session`` to handlers that get
    the rest of the line. They are handled by the harness, not sent to the model.
    """
    commands = commands or {}
    typer.echo("Interactive harness. Type /exit or /quit to leave"
               + (", /help for commands." if commands else "."))
    while True:
        try:
            question = input(prompt() if prompt else "You> ").strip()
        except EOFError:
            typer.echo("")
            return
        if question.lower() in {"/exit", "/quit"}:
            return
        if not question:
            continue
        if commands and question.startswith("/"):
            name, _, rest = question.partition(" ")
            if name == "/help":
                typer.echo("Commands: " + ", ".join(sorted([*commands, "/exit"])))
                continue
            if name in commands:
                try:
                    commands[name](rest.strip())
                except Exception as error:
                    typer.echo(f"Unable to run {name}: {error}", err=True)
                continue
            typer.echo(f"Unknown command {name}. Type /help for commands.")
            continue
        try:
            respond(question)
        except Exception as error:
            typer.echo(f"Unable to answer question: {error}", err=True)
