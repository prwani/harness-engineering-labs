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

2. Run a small planner → generator → separate evaluator flow and inspect its
   score and visited nodes:

   ```bash
   python - <<'PY'
   from harness.capstone import AblationConfig, EvaluationResult, build_capstone_graph, run_capstone
   from harness.graph import GraphState

   config = AblationConfig(planning=True, evaluation=True, max_refinements=1)
   graph = build_capstone_graph(
       config,
       lambda state: state.with_data(plan=["inspect product"]),
       lambda state: f"Draft based on {state.data['plan']}",
       lambda output, _state: EvaluationResult(True, "contains a plan", 1.0),
   )
   result = run_capstone(graph, config, GraphState())
   print("Visited:", " -> ".join(result.visited))
   print("Evaluator passed:", result.data["evaluation"].passed)
   PY
   ```

   The evaluator is a separate graph step, and the output makes the plan and
   evaluation path observable.
3. Run `pytest checks/test_capstone.py` for deterministic verification, then
   `pytest checks/` for the full regression suite.
4. Inspect the snapshot's declared capabilities with `harness lab-info`.
5. Optional: to try the live Foundry prompt, copy `.env.example` to `.env`,
   fill in the endpoint and deployment settings, and sign in with `az login`.
   Run `harness ask` to ask repeated questions and type `/exit` to leave; use
   `harness ask "<question>"` for one-shot use. Each question is an independent
   turn; the Python example above exercises this lab's capstone workflow.
   `ask` retains Lab 2B's repository and CLI tools behind the same
   `pre_tool`/`pre_model` hooks (shell denied; Git and Azure CLI limited to
   a few read commands), shows a spinner while it works, and ends each
   answer with the total time and a `Summary:` of LLM and tool calls.
   `--repo PATH` changes the tools' starting directory.

## External integrations

The following integration requires learner-provisioned credentials and resources;
this snapshot does not include a command to run it:
- full Foundry evaluation suite

All live paths must use Entra credentials and must not add API-key configuration.
