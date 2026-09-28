"""Loop taxonomy: retry, validation, polling and refinement loop contracts.

Each loop is a small, generic, deterministic contract the harness applies
around a call, independent of any specific tool or model. A model judge may
sit behind a validation loop's check, but the loop mechanics themselves
(cap, backoff, stop conditions) are ordinary code.
"""

from dataclasses import dataclass
from typing import Any, Callable, TypeVar
import time


T = TypeVar("T")


class LoopExhaustedError(Exception):
    """Raised when a loop reaches its cap without succeeding."""


@dataclass(frozen=True)
class RetryLoop:
    """Retries a flaky call with exponential backoff, for example on a
    503 from the provider."""

    max_attempts: int = 3
    base_delay: float = 0.0

    def run(self, call: Callable[[], T], is_retryable: Callable[[Exception], bool] = lambda _e: True) -> T:
        last_error: Exception | None = None
        for attempt in range(self.max_attempts):
            try:
                return call()
            except Exception as error:  # noqa: BLE001 - loop taxonomy is generic
                if not is_retryable(error):
                    raise
                last_error = error
                if attempt < self.max_attempts - 1 and self.base_delay:
                    time.sleep(self.base_delay * (2 ** attempt))
        raise LoopExhaustedError(f"retry loop exhausted after {self.max_attempts} attempts") from last_error


@dataclass(frozen=True)
class ValidationLoop:
    """Re-prompts until the output passes a validator, up to a rejection
    budget, then ends rather than looping forever."""

    max_rejections: int = 2

    def run(
        self,
        generate: Callable[[str | None], T],
        validate: Callable[[T], tuple[bool, str]],
    ) -> T:
        feedback: str | None = None
        for _ in range(self.max_rejections + 1):
            output = generate(feedback)
            ok, reason = validate(output)
            if ok:
                return output
            feedback = reason
        raise LoopExhaustedError(f"validation loop exceeded {self.max_rejections} rejections: {feedback}")


@dataclass(frozen=True)
class PollingLoop:
    """Polls a status function until it reports completion or a cap of
    attempts is reached."""

    max_attempts: int = 10
    interval: float = 0.0

    def run(self, poll: Callable[[], tuple[bool, T]]) -> T:
        for attempt in range(self.max_attempts):
            done, value = poll()
            if done:
                return value
            if attempt < self.max_attempts - 1 and self.interval:
                time.sleep(self.interval)
        raise LoopExhaustedError(f"polling loop exceeded {self.max_attempts} attempts")


@dataclass(frozen=True)
class RefinementLoop:
    """Iteratively improves a draft using a scoring function, stopping when
    the score stops improving or the cap is reached."""

    max_iterations: int = 3
    min_improvement: float = 0.0

    def run(
        self,
        draft: T,
        refine: Callable[[T, float], T],
        score: Callable[[T], float],
    ) -> T:
        best = draft
        best_score = score(draft)
        for _ in range(self.max_iterations):
            candidate = refine(best, best_score)
            candidate_score = score(candidate)
            if candidate_score - best_score <= self.min_improvement:
                break
            best, best_score = candidate, candidate_score
        return best
