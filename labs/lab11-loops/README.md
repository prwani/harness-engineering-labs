---
layout: default
title: "Lab 11 — Loop engineering"
---

# Lab 11 — Loop engineering

## Concept

Several earlier labs already built a loop informally — Lab 6's completion
check, Lab 7's retry-with-backoff. This lab names the pattern explicitly and
generalizes it: **every** loop in the harness (validation, retry, polling,
refinement) has the same anatomy, and that anatomy is what makes a loop safe
instead of runaway.

**Key ideas**
- A well-engineered loop always has: a **trigger**, an **evaluator**
  (rule-based, model-based, or hybrid), all **three exits** (success,
  failure, max-iterations), and a **state delta** each iteration — skipping
  any of the three exits, or repeating with identical state, is an
  anti-pattern this lab deliberately reproduces and fixes.
- **Validation** (service map must satisfy a schema plus cross-file citation
  checks) lives in the `on_stop` hook from Lab 6 — the loop code itself
  never changes, only what the hook checks.
- **Retry** generalizes Lab 7's `on_error` hook; **polling** waits on
  external state (e.g. an order backlog draining) with a hard deadline;
  **refinement** uses a hybrid evaluator — a rule checks citations, then a
  model judge (optionally a different model family) scores against a rubric
  with a calibrated threshold, so it can't loop forever chasing "better."
- Anti-patterns are drilled on purpose: unbounded polling, a judge that
  never says "good enough," identical-state retries, over-looping on
  questions a single call already answers, and compacting mid-loop without
  losing the schema or original task.

This self-contained snapshot starts from Lab 10 and introduces a first-cut,
offline-testable representation of its capability. It retains all earlier checks
and can be installed independently.

## Added in this lab

- [`harness/loops.py`](harness/loops.py) adds `RetryLoop`, `ValidationLoop`,
  `PollingLoop`, and `RefinementLoop` with bounded retry, feedback, polling,
  and improvement behavior; `LoopExhaustedError` marks unsuccessful exits.

## Learner steps

1. Create and activate a virtual environment, then install the lab:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

2. Simulate a transient failure and see the retry loop stop after success:

   ```bash
   python - <<'PY'
   from harness.loops import RetryLoop

   attempts = {"count": 0}
   def flaky_read():
       attempts["count"] += 1
       if attempts["count"] < 3:
           raise RuntimeError("temporary service error")
       return "read completed"

   print(RetryLoop(max_attempts=4).run(flaky_read))
   print("Attempts:", attempts["count"])
   PY
   ```

   The call succeeds on its third attempt; the cap prevents unbounded retries.
3. Run `pytest checks/test_loops.py` for deterministic verification, then
   `pytest checks/` for the full regression suite.
4. Inspect the snapshot's declared capabilities with `harness lab-info`.

## External integrations

The following integration requires learner-provisioned credentials and resources;
this snapshot does not include a command to run it:
- live retry and polling behavior

All live paths must use Entra credentials and must not add API-key configuration.
