from harness.capstone import AblationConfig, EvaluationResult, build_capstone_graph, entry_node, run_capstone
from harness.graph import GraphState


def _plan(state):
    return state.with_data(plan=["fix price"])


def _make_generate(outputs):
    calls = iter(outputs)

    def generate(_state):
        return next(calls)

    return generate


def test_entry_node_depends_on_planning_ablation():
    assert entry_node(AblationConfig(planning=True)) == "plan"
    assert entry_node(AblationConfig(planning=False)) == "generate"


def test_graph_passes_on_first_evaluation():
    config = AblationConfig(planning=True, evaluation=True, max_refinements=2)

    def evaluate(output, _state):
        return EvaluationResult(passed=True, feedback="looks good", score=1.0)

    graph = build_capstone_graph(config, _plan, _make_generate(["draft-1"]), evaluate)
    result = run_capstone(graph, config)

    assert result.data["output"] == "draft-1"
    assert result.data["evaluation"].passed
    assert result.visited == ("plan", "generate", "evaluate")


def test_evaluator_is_separate_from_generator_and_can_reject():
    config = AblationConfig(planning=False, evaluation=True, max_refinements=2)
    scores = iter([False, True])

    def evaluate(output, _state):
        passed = next(scores)
        return EvaluationResult(passed=passed, feedback="needs work" if not passed else "good", score=1.0 if passed else 0.0)

    graph = build_capstone_graph(config, _plan, _make_generate(["draft-1", "draft-2"]), evaluate)
    result = run_capstone(graph, config)

    assert result.data["output"] == "draft-2"
    assert result.data["refinements"] == 1
    assert result.data["evaluation"].passed


def test_refinement_stops_at_ablation_cap_even_if_never_passing():
    config = AblationConfig(planning=False, evaluation=True, max_refinements=1)

    def evaluate(_output, _state):
        return EvaluationResult(passed=False, feedback="never good enough", score=0.0)

    graph = build_capstone_graph(config, _plan, _make_generate(["d1", "d2", "d3"]), evaluate)
    result = run_capstone(graph, config)

    assert not result.data["evaluation"].passed
    assert result.data["refinements"] == 1


def test_disabling_evaluation_ablation_always_passes():
    config = AblationConfig(planning=False, evaluation=False)

    def evaluate(_output, _state):
        raise AssertionError("evaluator should not run when evaluation is disabled")

    graph = build_capstone_graph(config, _plan, _make_generate(["only-draft"]), evaluate)
    result = run_capstone(graph, config)

    assert result.data["evaluation"].passed


def test_ablation_metadata_is_recorded():
    config = AblationConfig(planning=True, evaluation=True, max_refinements=3)

    assert config.as_metadata() == {"planning": True, "evaluation": True, "max_refinements": 3}
