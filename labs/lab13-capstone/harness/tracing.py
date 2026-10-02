"""Observability for `harness ask`: an event stream per run, and a summary.

``harness ask --trace FILE`` appends one JSON object per line for every
step: the question, each model call (latency, tokens, stop reason, tools
requested), each tool call and result, hook decisions, permission
decisions, and the end of the run with totals. ``harness trace FILE``
folds those events into a summary table, like a log pipeline would.

Tracing is a side effect only: it never changes what the loop does.
Arguments and results are redacted and truncated before they are written,
because a trace, like a session, holds prompts and file contents.

Cost is an estimate from prices you supply, in USD per million tokens
(``--input-price``/``--output-price`` or ``HARNESS_PRICE_INPUT``/
``HARNESS_PRICE_OUTPUT``). Your Azure bill is the source of truth.
"""

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field, fields, replace
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
from time import perf_counter
from typing import Any

from harness.models.adapters import ModelClient, Turn
from harness.telemetry import redact

MAX_FIELD_CHARS = 500
_SECRET_ASSIGNMENT = re.compile(r"(?i)\b([A-Z0-9_]*(?:KEY|SECRET|TOKEN|PASSWORD)[A-Z0-9_]*)\s*=\s*\S+")


def scrub(value: Any) -> str:
    """Redact secrets and truncate, for anything written to a trace."""
    text = value if isinstance(value, str) else json.dumps(value, default=str)
    text = _SECRET_ASSIGNMENT.sub(r"\1=[REDACTED]", redact(text))
    return text if len(text) <= MAX_FIELD_CHARS else text[:MAX_FIELD_CHARS] + f"... ({len(text)} chars)"


def prices() -> tuple[float | None, float | None]:
    """USD per million input and output tokens, from the environment or the lab's .env."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    def read(name: str) -> float | None:
        value = os.environ.get(name)
        return float(value) if value else None

    return read("HARNESS_PRICE_INPUT"), read("HARNESS_PRICE_OUTPUT")


def estimate_cost(input_tokens: int, output_tokens: int,
                  input_price: float | None, output_price: float | None) -> float | None:
    if input_price is None or output_price is None:
        return None
    return input_tokens / 1e6 * input_price + output_tokens / 1e6 * output_price


class TraceWriter:
    """Appends events to a JSONL file."""

    def __init__(self, path: Path, session_id: str = "") -> None:
        self.path, self.session_id = path, session_id
        path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, event: str, **data: Any) -> None:
        record = {"ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                  "event": event, "session": self.session_id, **data}
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, default=str) + "\n")


@dataclass
class Meter:
    """Running totals for this process, plus the size of the last request."""

    model_calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    model_seconds: float = 0.0
    last_input_tokens: int = 0
    last_request: dict[str, int] = field(default_factory=dict)


class MeteredClient:
    """Wraps a model client to measure every call; the call itself is unchanged."""

    def __init__(self, client: ModelClient, meter: Meter, trace: TraceWriter | None = None) -> None:
        self.client, self.meter, self.trace = client, meter, trace

    def complete(self, *, system: str, messages: list[dict[str, Any]],
                 tools: list[dict[str, Any]], **kwargs: Any) -> Turn:
        started = perf_counter()
        try:
            turn = self.client.complete(system=system, messages=messages, tools=tools, **kwargs)
        except Exception as error:
            if self.trace:
                self.trace.write("model_error", seconds=round(perf_counter() - started, 3), error=scrub(str(error)))
            raise
        seconds = perf_counter() - started
        usage, meter = turn.usage, self.meter
        meter.model_calls += 1
        meter.input_tokens += usage.input_tokens
        meter.output_tokens += usage.output_tokens
        meter.cached_tokens += usage.cached_tokens
        meter.model_seconds += seconds
        meter.last_input_tokens = usage.input_tokens
        tool_results = sum(len(json.dumps(m["content"], default=str)) for m in messages if m["role"] == "tool")
        meter.last_request = {
            "system_chars": len(system),
            "tools_chars": len(json.dumps(tools)),
            "messages": len(messages),
            "message_chars": sum(len(json.dumps(m["content"], default=str)) for m in messages),
            "tool_result_chars": tool_results,
        }
        if self.trace:
            self.trace.write(
                "model_call", n=meter.model_calls, seconds=round(seconds, 3), stop=turn.stop,
                input_tokens=usage.input_tokens, output_tokens=usage.output_tokens,
                cached_tokens=usage.cached_tokens, tool_calls=[call.name for call in turn.tool_calls],
            )
        return turn


def chain(first: Callable[..., Any], second: Callable[..., Any] | None) -> Callable[..., Any]:
    def both(*args: Any) -> Any:
        first(*args)
        return second(*args) if second else None
    return both


def traced_events(events: Any, trace: TraceWriter) -> Any:
    """The same events, with each one also written to the trace."""
    recorders = {
        "on_tool_call": lambda name, args: trace.write("tool_call", tool=name, args=scrub(args)),
        "on_hook_denial": lambda name, reason: trace.write("denied", tool=name, reason=scrub(reason)),
        "on_hook_feedback": lambda name, message: trace.write("hook", tool=name, message=scrub(message)),
        "on_permission": lambda name, args, decision, why: trace.write(
            "permission", tool=name, decision=decision, why=why),
    }
    names = {item.name for item in fields(events)}
    return replace(events, **{name: chain(record, getattr(events, name))
                              for name, record in recorders.items() if name in names})


def trace_results(trace: TraceWriter) -> Callable[[dict[str, Any]], None]:
    """An on_message callback that records each tool result's outcome and size."""

    def record(message: dict[str, Any]) -> None:
        if message["role"] != "tool":
            return
        for result in message["content"]:
            output = str(result["output"])
            status = "denied" if output.startswith("DENIED:") else "error" if output.startswith("ERROR:") else "ok"
            trace.write("tool_result", call_id=result["call_id"], status=status, chars=len(output),
                        preview=scrub(output[:200]))

    return record


def summarize(path: Path, input_price: float | None = None, output_price: float | None = None) -> str:
    """Fold a trace file into a summary table."""
    events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not events:
        return f"{path}: no events"
    count = Counter(event["event"] for event in events)
    calls = [event for event in events if event["event"] == "model_call"]
    tools = Counter(event["tool"] for event in events if event["event"] == "tool_call")
    results = Counter(event["status"] for event in events if event["event"] == "tool_result")
    permissions = Counter(event["decision"] for event in events if event["event"] == "permission")
    ends = [event for event in events if event["event"] == "run_end"]
    tokens_in = sum(event["input_tokens"] for event in calls)
    tokens_out = sum(event["output_tokens"] for event in calls)
    cost = estimate_cost(tokens_in, tokens_out, input_price, output_price)
    rows = [
        ("runs", f"{count['run_start']} started, {len(ends)} finished"),
        ("llm calls", f"{len(calls)} ({sum(event['seconds'] for event in calls):.1f}s)"),
        ("tokens", f"input={tokens_in}, output={tokens_out}, "
                   f"cached={sum(event['cached_tokens'] for event in calls)}"),
        ("tool calls", ", ".join(f"{name}={n}" for name, n in tools.most_common()) or "none"),
        ("tool results", ", ".join(f"{name}={n}" for name, n in sorted(results.items())) or "none"),
        ("hook events", f"denied={count['denied']}, feedback={count['hook']}"),
        ("permissions", ", ".join(f"{name}={n}" for name, n in sorted(permissions.items())) or "none"),
        ("duration", f"{sum(event.get('seconds', 0) for event in ends):.1f}s"),
        ("estimated cost", f"${cost:.4f}" if cost is not None else
         "n/a (set --input-price and --output-price, USD per 1M tokens)"),
    ]
    if errors := [event for event in ends if event.get("error")]:
        rows.append(("errors", "; ".join(event["error"] for event in errors)))
    width = max(len(name) for name, _ in rows)
    return "\n".join(f"{name:<{width}}  {value}" for name, value in rows)


def describe_cost(meter: Meter) -> str:
    """What `/cost` prints: totals for this process."""
    cost = estimate_cost(meter.input_tokens, meter.output_tokens, *prices())
    estimate = f"${cost:.4f} (estimate)" if cost is not None else \
        "n/a (set HARNESS_PRICE_INPUT and HARNESS_PRICE_OUTPUT, USD per 1M tokens)"
    return (f"LLM calls: {meter.model_calls} ({meter.model_seconds:.1f}s)\n"
            f"Tokens: input={meter.input_tokens}, output={meter.output_tokens}, cached={meter.cached_tokens}\n"
            f"Cost: {estimate}")


def describe_context(meter: Meter, messages: list[dict[str, Any]] | None = None) -> str:
    """What `/context` prints: what the last request was made of (about 4 characters per token)."""
    request = meter.last_request
    now = ""
    if messages is not None:
        chars = sum(len(json.dumps(m.get("content", ""), default=str)) for m in messages)
        now = f"\nHistory now: {len(messages)} messages, ~{chars // 4} tokens"
    if not request:
        return "No model call yet in this process." + now
    other = request["message_chars"] - request["tool_result_chars"]
    return "\n".join([
        f"Last request: {meter.last_input_tokens} input tokens reported by the model",
        f"  system prompt     ~{request['system_chars'] // 4} tokens",
        f"  tool definitions  ~{request['tools_chars'] // 4} tokens",
        f"  messages          ~{other // 4} tokens in {request['messages']} messages",
        f"  tool results      ~{request['tool_result_chars'] // 4} tokens",
    ]) + now
