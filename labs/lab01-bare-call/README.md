---
layout: default
title: "Lab 1 — Bare model call"
---

# Lab 1 — Bare model call

## Concept

This is the control group: a call that is stateless, has no tools, and has no
memory. It exists to make the *next* lab's improvement measurable, and to make
one thing obvious — the model must **act**, not just describe what it thinks
is happening.

The task (M1) asks the model to inspect and report on a small, broken online
store. With no tools, it can only guess: it invents plausible-looking ports
and env vars, misses real issues, and claims to have "fixed" things it never
touched. A deterministic scorecard (accuracy against a known answer key,
plus a fabrication check against the simulator's write log) makes these
failures explicit instead of impressionistic.

**Key ideas**
- A bare call has no way to *find out* anything — it can only pattern-match
  from training data onto a task it has never actually seen.
- The `StoreHealthReport` envelope is the contract the grader checks against;
  a malformed response is itself a scored failure.
- The fabrication check cross-references every "fixed" claim against the
  simulator's write log — claiming success is not the same as achieving it.
- This run's scorecard becomes the baseline every later lab's `harness eval`
  is compared against.

This self-contained snapshot starts from Lab 0 and introduces a first-cut,
offline-testable representation of its capability. It retains all earlier checks
and can be installed independently.

## Offline verification

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest checks/
harness lab-info
```

## Live validation (not run locally)

The following integrations require learner-provisioned credentials and resources:

- Foundry bare-call evaluation

All live paths must use Entra credentials and must not add API-key configuration.
