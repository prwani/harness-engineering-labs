---
layout: default
title: "Lab 13 — Planner, generator, evaluator capstone"
---

# Lab 13 — Planner, generator, evaluator capstone

## Concept

The capstone composes nearly every prior lab into one system: a **dynamic**
graph (Lab 12's static/dynamic distinction resolved in favor of dynamic) run
by three specialized agents — planner, generator, evaluator — coordinated
through files, loops, and fan-out, with an ablation study to find out which
pieces actually matter.

**Key ideas**
- Three agent specs, one harness: `planner` reads the catalog and writes a
  per-product plan **at runtime** — the graph's nodes are created from data,
  which is what makes it dynamic rather than a fixed set of branches.
- `generator` mounts the Lab 8 `product-description` skill and fans out over
  parallel edges (reusing the Lab 9 spawner); a separate, deliberately
  **sceptical** `evaluator` — using a different model family than the
  generator — scores each result against a calibrated rubric with hard
  thresholds.
- A **refinement loop** (Lab 11's anatomy) runs each item until it passes,
  a round cap is hit, or there's no more progress; agents hand off state
  through per-item contract files, not shared memory.
- **Ablation is the point:** remove one component at a time — an *agent*
  (planner, evaluator) or a *harness feature* (approval, skills, tool
  search, compaction) — and re-run the eval suite across model families to
  see what's actually load-bearing for today's models, and whether the value
  lost lives in the runtime or in an agent definition.

This self-contained snapshot starts from Lab 12 and introduces a first-cut,
offline-testable representation of its capability. It retains all earlier checks
and can be installed independently.

## Added in this lab

- [`harness/capstone.py`](harness/capstone.py) adds `AblationConfig` and
  `build_capstone_graph()` to compose planning, generation, and separate
  evaluation nodes with a configurable refinement route.
- The same module adds `run_capstone()` for graph execution and `AblationRun`
  for summarizing the enabled capabilities and result.

## Learner steps

1. Create and activate a virtual environment, then install the lab:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

2. Run the focused test for this lab's capstone behavior: `pytest checks/test_capstone.py`.
   It uses deterministic fixtures, so it runs offline.
3. Run all checks for this snapshot and earlier labs: `pytest checks/`.
4. Inspect the snapshot's declared capabilities: `harness lab-info`.

## External integrations

The following integration requires learner-provisioned credentials and resources;
this snapshot does not include a command to run it:
- full Foundry evaluation suite

All live paths must use Entra credentials and must not add API-key configuration.
