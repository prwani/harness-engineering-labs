"""Capstone: a dynamic planner-generator-evaluator graph with a separate
evaluator and ablation metadata.

The graph is built dynamically from an ablation configuration: which
layers (planning, evaluation, retry) are switched on for this run. The
evaluator is a separate node/agent from the generator, so grading is never
self-graded. Ablation metadata records exactly which capabilities were
enabled, so runs can be compared like the `h1`..`h14` progression.
"""

from dataclasses import dataclass, field
from typing import Any, Callable

from harness.graph import Graph, GraphState


@dataclass(frozen=True)
class AblationConfig:
    """Which capabilities are switched on for this capstone run."""

    planning: bool = True
    evaluation: bool = True
    max_refinements: int = 1

    def as_metadata(self) -> dict[str, Any]:
        return {
            "planning": self.planning,
            "evaluation": self.evaluation,
            "max_refinements": self.max_refinements,
        }


@dataclass(frozen=True)
class EvaluationResult:
    passed: bool
    feedback: str
    score: float


Generator = Callable[[GraphState], str]
Evaluator = Callable[[str, GraphState], EvaluationResult]


def build_capstone_graph(
    config: AblationConfig,
    plan: Callable[[GraphState], GraphState],
    generate: Generator,
    evaluate: Evaluator,
) -> Graph:
    """Builds the planner -> generator -> evaluator graph, dynamically
    including or skipping the planning node based on the ablation config."""
    graph = Graph()

    def generator_node(state: GraphState) -> GraphState:
        output = generate(state)
        refinements = state.data.get("refinements", 0)
        if "evaluation" in state.data:
            refinements += 1
        return state.with_data(output=output, refinements=refinements)

    def evaluator_node(state: GraphState) -> GraphState:
        if not config.evaluation:
            return state.with_data(evaluation=EvaluationResult(True, "evaluation disabled", 1.0))
        result = evaluate(state.data["output"], state)
        return state.with_data(evaluation=result)

    def route_from_evaluator(state: GraphState) -> str:
        evaluation: EvaluationResult = state.data["evaluation"]
        refinements = state.data.get("refinements", 0)
        if evaluation.passed or refinements >= config.max_refinements:
            return "END"
        return "generate"

    graph.add_node("generate", generator_node)
    graph.add_node("evaluate", evaluator_node)
    graph.add_route("generate", lambda _state: "evaluate")
    graph.add_route("evaluate", route_from_evaluator)

    if config.planning:
        def planner_node(state: GraphState) -> GraphState:
            return plan(state)

        graph.add_node("plan", planner_node)
        graph.add_route("plan", lambda _state: "generate")

    return graph


def entry_node(config: AblationConfig) -> str:
    return "plan" if config.planning else "generate"


def run_capstone(graph: Graph, config: AblationConfig, state: GraphState | None = None) -> GraphState:
    """Runs the capstone graph. Each visit gets a distinct idempotency key
    (node name plus visit count) so the generate/evaluate refinement loop
    can safely repeat nodes without being treated as a crash replay."""
    state = state or GraphState()
    return graph.run(
        entry_node(config),
        state,
        idempotency_key=lambda name, current: f"{name}:{len(current.visited)}",
    )


@dataclass
class AblationRun:
    config: AblationConfig
    result: GraphState

    def summary(self) -> dict[str, Any]:
        evaluation: EvaluationResult = self.result.data.get("evaluation")
        return {
            "ablation": self.config.as_metadata(),
            "passed": evaluation.passed if evaluation else None,
            "score": evaluation.score if evaluation else None,
            "visited": list(self.result.visited),
        }
