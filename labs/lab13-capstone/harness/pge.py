"""`harness pge`: planner -> human gate -> generator -> evaluator, bounded.

    planner (read-only) -> PLAN.md -> human approves (and may edit PLAN.md)
      -> generator (edit files, run tests)
      -> evaluator (fresh context: read, run tests, read-only git; JSON verdict)
      -> FAIL: back to the generator with the evaluator's feedback, at most
         ``max_revisions`` times; PASS: the human reviews the diff and commits.

Each role is an agent (Lab 9) with its own prompt and tool list, behind the
project's hooks and permissions. Nobody is there to answer a prompt, so a
call that would ask is denied; the generator runs with edits accepted. The
evaluator starts from an empty history: it sees the plan, the code and the
test results, never the generator's reasoning. Nothing is committed.
"""

from collections.abc import Callable
from contextlib import AbstractContextManager, nullcontext
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
import re
from typing import TYPE_CHECKING, Any

from harness.agents import AgentDefinition
from harness.models.adapters import ModelClient

if TYPE_CHECKING:
    from harness.chat import Events


def _role(name: str, tools: str, prompt: str) -> AgentDefinition:
    return AgentDefinition(name=name, description=f"{name} role",
                           tools=tuple(tool.strip() for tool in tools.split(",")),
                           prompt=prompt, path=Path(f"<pge {name}>"), scope="graph")


PLANNER = _role(
    "planner", "list_files, read_file, git_status, git_log",
    "You plan features for this codebase; you cannot change files. Read the code and write "
    "an implementation plan in Markdown with sections: Goal, Files to change, Steps, "
    "Acceptance criteria (numbered, each one objectively checkable, including the exact "
    "pytest tests that must exist and pass). Reply with only the plan.")
GENERATOR = _role(
    "generator", "list_files, read_file, write_file, edit_file, run_tests",
    "You implement PLAN.md in this codebase. Follow the plan exactly, keep changes focused, "
    "and run the tests until they pass. Do not commit.")
EVALUATOR = _role(
    "evaluator", "list_files, read_file, run_tests, git_status, git_cli",
    "You are a strict reviewer who did not write this code. Compare the working-tree changes "
    "(git_cli diff, plus new untracked files from git_status) against every acceptance "
    "criterion in PLAN.md. Run the tests yourself. A criterion passes only with evidence. "
    'Reply with only a JSON object: {"verdict": "PASS" or "FAIL", "failed_criteria": '
    '["..."], "feedback": "..."}.')


@dataclass
class Verdict:
    verdict: str
    failed_criteria: list[str]
    feedback: str


def parse_verdict(text: str) -> Verdict:
    """The evaluator's JSON verdict; anything else counts as FAIL."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    try:
        data = json.loads(match.group(0)) if match else None
    except json.JSONDecodeError:
        data = None
    if not isinstance(data, dict) or data.get("verdict") not in {"PASS", "FAIL"}:
        return Verdict("FAIL", ["evaluator output"],
                       f"The evaluator did not return a JSON verdict: {text.strip()[:300]!r}")
    failed = data.get("failed_criteria") or []
    return Verdict(data["verdict"], [str(item) for item in failed] if isinstance(failed, list)
                   else [str(failed)], str(data.get("feedback", "")))


@dataclass
class NodeRun:
    name: str
    model_calls: int
    tool_calls: int
    denied: int
    text: str


@dataclass
class PGEResult:
    outcome: str  # PASS, FAIL, STOPPED (plan rejected) or UNCHECKED (no evaluator)
    plan: Path
    nodes: list[NodeRun] = field(default_factory=list)
    verdicts: list[Verdict] = field(default_factory=list)
    trace: Path | None = None


def generator_task(feedback: str = "") -> str:
    task = "Implement PLAN.md exactly. Run the tests until they pass. Do not commit."
    if feedback:
        task += ("\nAn independent evaluator rejected the previous attempt:\n"
                 f"{feedback}\nFix only what it reports.")
    return task


def run_pge(
    client: ModelClient,
    feature: str,
    repo: Path,
    *,
    approve_plan: Callable[[Path], bool],
    max_revisions: int = 2,
    evaluate: bool = True,
    runs_dir: Path | None = None,
    node_events: Callable[[str], AbstractContextManager["Events"]] | None = None,
    on_node_done: Callable[[NodeRun], None] | None = None,
    on_verdict: Callable[[str, Verdict], None] | None = None,
) -> PGEResult:
    from harness.chat import Events
    from harness.learner import ask_with_tools
    from harness.permissions import Permissions
    from harness.tool_loop import LoopStats
    from harness.tracing import Meter, MeteredClient, TraceWriter, trace_results, traced_events

    trace = None
    if runs_dir is not None:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        trace = TraceWriter(runs_dir / f"pge-{stamp}.jsonl", "pge")
        client = MeteredClient(client, Meter(), trace)
        trace.write("run_start", question=feature[:500], mode="pge", repo=str(repo))
    result = PGEResult("FAIL", repo / "PLAN.md", trace=trace.path if trace else None)

    def node(name: str, agent: AgentDefinition, task: str, *, accept_edits: bool = False) -> str:
        on_message, stats = None, LoopStats()
        if trace:
            trace.write("node", node=name)
            on_message = trace_results(trace)
        # The caller can show progress per node (and nothing is shown during the human gate).
        with (node_events(name) if node_events else nullcontext(Events())) as callbacks:
            if trace:
                callbacks = traced_events(callbacks, trace)
            turn = ask_with_tools(client, task, repo=repo, stats=stats, on_message=on_message,
                                  permissions=Permissions.load(repo, accept_edits=accept_edits),
                                  agent=agent, **callbacks.as_kwargs())
        run = NodeRun(name, stats.model_calls, stats.tool_calls, stats.denied_calls, turn.text)
        result.nodes.append(run)
        if on_node_done:
            on_node_done(run)
        return turn.text

    plan = node("planner", PLANNER, f"Feature request: {feature}")
    result.plan.write_text(plan.strip() + "\n", encoding="utf-8")
    if not approve_plan(result.plan):
        result.outcome = "STOPPED"
    else:
        feedback = ""
        for round_number in range(max_revisions + 1):
            node(f"generator-{round_number}", GENERATOR, generator_task(feedback), accept_edits=True)
            if not evaluate:
                result.outcome = "UNCHECKED"
                break
            verdict = parse_verdict(node(f"evaluator-{round_number}", EVALUATOR,
                                         "Evaluate the implementation of PLAN.md."))
            result.verdicts.append(verdict)
            if trace:
                trace.write("verdict", round=round_number, verdict=verdict.verdict,
                            failed_criteria=verdict.failed_criteria)
            if on_verdict:
                on_verdict(f"evaluator-{round_number}", verdict)
            if verdict.verdict == "PASS":
                result.outcome = "PASS"
                break
            feedback = f"Failed criteria: {verdict.failed_criteria}\n{verdict.feedback}"
    if trace:
        trace.write("run_end", outcome=result.outcome,
                    llm_calls=sum(run.model_calls for run in result.nodes),
                    tool_calls=sum(run.tool_calls for run in result.nodes),
                    denied=sum(run.denied for run in result.nodes))
    return result
