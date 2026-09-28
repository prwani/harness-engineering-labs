"""OpenTelemetry-style span/event model, cost attribution, redaction and
prompt-cache boundaries.

Tracing must not change behaviour: spans are recorded as a side effect only.
Every reasoning step, tool call, token spend and latency is a span. Costs are
attributed per task, per agent and per tool from the Ledger's usage. A
``post_tool`` hook redacts secrets before results are stored or traced.
"""

from dataclasses import dataclass, field
from typing import Any
import re
import time

from harness.ledger import Usage

# $ per 1K tokens, input/output, keyed by provider. Illustrative, not billing-accurate.
PRICE_PER_1K = {
    "claude": {"input": 0.003, "output": 0.015},
    "gpt": {"input": 0.005, "output": 0.015},
}

_REDACT_PATTERNS = [
    re.compile(r'"Authorization"\s*:\s*"[^"]*"', re.IGNORECASE),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]+"),
    re.compile(r'"api[_-]?key"\s*:\s*"[^"]*"', re.IGNORECASE),
]


@dataclass
class Span:
    name: str
    attributes: dict[str, Any] = field(default_factory=dict)
    start: float = field(default_factory=time.monotonic)
    end: float | None = None
    children: list["Span"] = field(default_factory=list)

    def close(self) -> None:
        self.end = time.monotonic()

    @property
    def duration(self) -> float:
        return (self.end or time.monotonic()) - self.start

    def child(self, name: str, **attributes: Any) -> "Span":
        span = Span(name=name, attributes=attributes)
        self.children.append(span)
        return span


@dataclass
class Tracer:
    """Builds the span tree: agent.run -> agent.iteration -> gen_ai.chat / tool.execute."""

    root: Span | None = None

    def start_run(self, task: str) -> Span:
        self.root = Span(name="agent.run", attributes={"task": task})
        return self.root

    def flatten(self) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []

        def walk(span: Span) -> None:
            events.append({"name": span.name, "attributes": span.attributes, "duration": span.duration})
            for child in span.children:
                walk(child)

        if self.root:
            walk(self.root)
        return events


def cost_for(usage: Usage, provider: str) -> float:
    """Attribute a cost in dollars to reported usage."""
    prices = PRICE_PER_1K.get(provider, PRICE_PER_1K["claude"])
    return (usage.input_tokens / 1000) * prices["input"] + (usage.output_tokens / 1000) * prices["output"]


def redact(text: str) -> str:
    """Strip secrets and Authorization headers out of a tool result before
    it is stored or traced."""
    redacted = text
    for pattern in _REDACT_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


@dataclass(frozen=True)
class CacheBoundary:
    """Marks a stable prefix of the system prompt / tools as a cache
    breakpoint so repeated turns can reuse the provider's prompt cache."""

    label: str
    token_estimate: int


def cache_breakpoints(system: str, tools: list[dict[str, Any]]) -> list[CacheBoundary]:
    boundaries = [CacheBoundary("system", len(system) // 4)]
    if tools:
        boundaries.append(CacheBoundary("tools", sum(len(str(tool)) for tool in tools) // 4))
    return boundaries
