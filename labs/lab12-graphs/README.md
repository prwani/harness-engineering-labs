---
layout: default
title: "Lab 12 — Graph engineering"
---

# Lab 12 — Graph engineering

## Concept

A linear chain of steps ("fetch → compute → format → summarize") wastes calls
on steps that don't apply and can't retry one step without redoing the whole
chain. This lab replaces the chain with a typed **graph**: named node types,
typed edges, and the recognition that a **loop-back edge *is* a loop** — so
every rule from Lab 11 (trigger, evaluator, three exits, state delta) applies
to it unchanged.

**Key ideas**
- **Node types:** Action, Decision, Fan-out, Join/Merge, Human-in-the-loop,
  Loop-back. **Edge types:** Conditional, Parallel, Loop-back.
- A **Decision** node (a cheap router call, with a rule-based fallback) picks
  between two Action nodes — one for code questions, one for data
  questions — instead of running every step on every request.
- Lab 11's validation and refinement loops become **loop-back edges** with
  the same exits as before (success, repeated errors, max attempts); retry
  and polling stay inside a node's own tools.
- **Static vs. dynamic graphs:** static/compiled graphs (this lab) suit
  known branches, auditability, and predictable cost; dynamic graphs (built
  in Lab 13) suit work whose shape depends on the data.
- **Secure code execution** is tested adversarially: the same "revenue by
  product" computation runs on `local` and on ACA Dynamic Sessions, then a
  planted snippet tries to read `/etc/passwd`, reach the internet, and read
  harness credentials — it escapes locally and is contained on ACA, because
  credentials were never inside the sandbox to begin with.
- A **repository knowledge graph** (services, files, env vars, queues,
  manifests) is compared against grep and BM25 retrieval on accuracy, tokens,
  and citation validity for code questions.
- This is the **Lab 2C checkpoint**: the trace shows the branch taken, the
  loop-back retries, and why each loop exited.

This self-contained snapshot starts from Lab 11 and introduces a first-cut,
offline-testable representation of its capability. It retains all earlier checks
and can be installed independently.

## Added in this lab

- [`harness/graph.py`](harness/graph.py) adds `GraphState` to track data,
  visited nodes, and executed keys.
- `Graph.add_node()`, `Graph.add_route()`, and `Graph.run()` in the same file
  introduce conditional routing, replay protection, and optional human route
  confirmation.

## Learner steps

1. Create and activate a virtual environment, then install the lab:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

2. Run a graph that routes based on the request, then inspect the visited path:

   ```bash
   python - <<'PY'
   from harness.graph import Graph, GraphState

   graph = Graph()
   graph.add_node("classify", lambda state: state.with_data(kind="code"))
   graph.add_node("code", lambda state: state.with_data(answer="inspect repository"))
   graph.add_node("data", lambda state: state.with_data(answer="inspect catalog"))
   graph.add_route("classify", lambda state: state.data["kind"])
   graph.add_route("code", lambda _state: "END")
   graph.add_route("data", lambda _state: "END")
   result = graph.run("classify", GraphState())
   print("Route:", " -> ".join(result.visited))
   print("Answer:", result.data["answer"])
   PY
   ```

   Only the matching branch runs; the other branch remains unvisited.
3. Run `pytest checks/test_graph.py` for deterministic verification, then
   `pytest checks/` for the full regression suite.
4. Inspect the snapshot's declared capabilities with `harness lab-info`.
5. Optional: to try the live Foundry prompt, copy `.env.example` to `.env`,
   fill in the endpoint and deployment settings, and sign in with `az login`.
   Run `harness ask` to ask repeated questions and type `/exit` to leave; use
   `harness ask "<question>"` for one-shot use. Each question is an independent
   turn; the Python example above exercises this lab's graph feature.

## External integrations

The following integration requires learner-provisioned credentials and resources;
this snapshot does not include a command to run it:
- ACA code executor

All live paths must use Entra credentials and must not add API-key configuration.
