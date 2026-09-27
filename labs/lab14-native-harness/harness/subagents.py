"""Sub-agent task model, parallel fan-out planning, and isolated child
transcripts.

A background agent runs a narrow task with its own isolated ``Session``
(its own transcript), never sharing history with the parent. The harness
builds a fan-out plan of independent sub-tasks and enforces a concurrency
cap so parallel spawns can't be used to bypass the approval or budget
policy.
"""

from dataclasses import dataclass, field
from typing import Any, Callable
from uuid import uuid4


class ConcurrencyCapError(Exception):
    """Raised when a fan-out plan exceeds the configured concurrency cap."""


@dataclass(frozen=True)
class SubAgentTask:
    task_id: str
    description: str
    tools: tuple[str, ...] = ()


def make_task(description: str, tools: tuple[str, ...] = ()) -> SubAgentTask:
    return SubAgentTask(task_id=uuid4().hex, description=description, tools=tools)


@dataclass
class FanOutPlan:
    """A set of independent sub-tasks, capped so a burst of parallel
    ``spawn_agent`` calls can't exceed the configured concurrency."""

    tasks: list[SubAgentTask] = field(default_factory=list)
    concurrency_cap: int = 4

    def add(self, task: SubAgentTask) -> None:
        self.tasks.append(task)

    def batches(self) -> list[list[SubAgentTask]]:
        return [
            self.tasks[i : i + self.concurrency_cap]
            for i in range(0, len(self.tasks), self.concurrency_cap)
        ]

    def check_cap(self, requested: int) -> None:
        if requested > self.concurrency_cap:
            raise ConcurrencyCapError(
                f"requested {requested} parallel spawns exceeds cap of {self.concurrency_cap}"
            )


@dataclass
class ChildTranscript:
    """A sub-agent's isolated transcript. It never sees the parent's
    messages and the parent never sees the child's raw transcript, only its
    final result."""

    task_id: str
    messages: list[dict[str, Any]] = field(default_factory=list)

    def append(self, message: dict[str, Any]) -> None:
        self.messages.append(message)


@dataclass
class SubAgentResult:
    task_id: str
    output: str


def run_sub_agent(
    task: SubAgentTask, runner: Callable[[SubAgentTask, ChildTranscript], str]
) -> SubAgentResult:
    """Execute one sub-agent task against its own isolated transcript."""
    transcript = ChildTranscript(task_id=task.task_id)
    transcript.append({"role": "user", "content": task.description})
    output = runner(task, transcript)
    transcript.append({"role": "assistant", "content": output})
    return SubAgentResult(task_id=task.task_id, output=output)


def run_fan_out(
    plan: FanOutPlan, runner: Callable[[SubAgentTask, ChildTranscript], str]
) -> list[SubAgentResult]:
    """Run every task in the plan, one concurrency-capped batch at a time,
    each with its own isolated transcript."""
    results: list[SubAgentResult] = []
    for batch in plan.batches():
        plan.check_cap(len(batch))
        for task in batch:
            results.append(run_sub_agent(task, runner))
    return results
