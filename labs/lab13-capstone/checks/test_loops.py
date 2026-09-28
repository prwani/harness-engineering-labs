import pytest

from harness.loops import LoopExhaustedError, PollingLoop, RefinementLoop, RetryLoop, ValidationLoop


def test_retry_loop_succeeds_after_transient_failures():
    calls = {"count": 0}

    def flaky():
        calls["count"] += 1
        if calls["count"] < 3:
            raise RuntimeError("503")
        return "ok"

    result = RetryLoop(max_attempts=5).run(flaky)

    assert result == "ok"
    assert calls["count"] == 3


def test_retry_loop_raises_non_retryable_errors_immediately():
    def always_fails():
        raise ValueError("bad request")

    with pytest.raises(ValueError):
        RetryLoop(max_attempts=3).run(always_fails, is_retryable=lambda e: not isinstance(e, ValueError))


def test_retry_loop_exhausts_after_cap():
    def always_fails():
        raise RuntimeError("503")

    with pytest.raises(LoopExhaustedError):
        RetryLoop(max_attempts=2).run(always_fails)


def test_validation_loop_returns_first_valid_output():
    attempts = {"count": 0}

    def generate(_feedback):
        attempts["count"] += 1
        return {"valid": attempts["count"] >= 2}

    def validate(output):
        return output["valid"], "invalid schema"

    result = ValidationLoop(max_rejections=2).run(generate, validate)

    assert result == {"valid": True}
    assert attempts["count"] == 2


def test_validation_loop_ends_after_rejection_budget():
    def generate(_feedback):
        return {"valid": False}

    def validate(output):
        return output["valid"], "always invalid"

    with pytest.raises(LoopExhaustedError, match="always invalid"):
        ValidationLoop(max_rejections=1).run(generate, validate)


def test_polling_loop_returns_once_done():
    state = {"tries": 0}

    def poll():
        state["tries"] += 1
        return state["tries"] >= 3, state["tries"]

    result = PollingLoop(max_attempts=5).run(poll)

    assert result == 3


def test_polling_loop_gives_up_after_cap():
    def poll():
        return False, None

    with pytest.raises(LoopExhaustedError):
        PollingLoop(max_attempts=2).run(poll)


def test_refinement_loop_stops_when_improvement_plateaus():
    scores = iter([1.0, 2.0, 2.0])

    def refine(draft, _score):
        return draft + 1

    def score(_draft):
        return next(scores)

    result = RefinementLoop(max_iterations=5).run(0, refine, score)

    assert result == 1
