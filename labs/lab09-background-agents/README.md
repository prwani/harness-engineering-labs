---
layout: default
title: "Lab 9 — Background agents and delegation"
---

# Lab 9 — Background agents and delegation

## Concept

A single agent mapping all 8 services of the sample app runs past its
context budget — the task simply doesn't fit in one run. This lab splits it:
an **orchestrator** agent spawns disposable **sub-agent** children, one per
service, each with its own small context, and merges their results
deterministically.

**Key ideas**
- Spawning, concurrency caps, timeouts, and result collection are **harness**
  features; the orchestrator and child specs only say *who* does *what* — a
  direct instance of the harness/agent split from Lab 2.
- **Fan-out vs. sequential is a real trade-off, not just "parallel is
  better":** true dependencies (one service needs another's output first)
  must stay sequential edges; shared-state writes need the Lab 5 optimistic
  concurrency check to avoid lost updates; parallel saves wall-clock but not
  necessarily tokens.
- The merged result is **deterministic regardless of completion order** —
  merging by spec order/service name, not arrival order, keeps parallel and
  sequential runs byte-comparable.
- **Failure isolation:** one child timing out produces a partial result with
  a flag, not a failed whole run.
- **Part B (★, scaling compute):** the same pattern runs on real ACA
  Sandboxes — one isolated sandbox per child, snapshot/resume checkpointing,
  per-sandbox egress policy, and multi-tenant isolation, showing the same
  orchestration idea holding up under real infrastructure constraints.

This self-contained snapshot starts from Lab 8 and introduces a first-cut,
offline-testable representation of its capability. It retains all earlier checks
and can be installed independently.

## Added in this lab

- [`harness/subagents.py`](harness/subagents.py) adds `SubAgentTask` and
  `ChildTranscript` for isolated child work, plus `run_sub_agent()` to execute it.
- The same module adds `FanOutPlan` and `run_fan_out()` to group tasks into
  concurrency-capped batches.

## Learner steps

1. Create and activate a virtual environment, then install the lab:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

2. Split a repository-mapping task across independent child agents:

   ```bash
   python - <<'PY'
   from harness.subagents import FanOutPlan, make_task, run_fan_out

   plan = FanOutPlan(concurrency_cap=2)
   for service in ("product", "order", "makeline"):
       plan.add(make_task(f"Map the {service} service"))
   results = run_fan_out(plan, lambda task, _transcript: f"Completed: {task.description}")
   for result in results:
       print(result.output)
   print("Batch sizes:", [len(batch) for batch in plan.batches()])
   PY
   ```

   Each task gets an isolated transcript, and the three tasks are split into
   batches that respect the concurrency cap.
3. Run `pytest checks/test_subagents.py` for deterministic verification, then
   `pytest checks/` for the full regression suite.
4. Inspect the snapshot's declared capabilities with `harness lab-info`.
5. Optional: to try the live Foundry prompt, copy `.env.example` to `.env`,
   fill in the endpoint and deployment settings, and sign in with `az login`.
   Run `harness ask` to ask repeated questions and type `/exit` to leave; use
   `harness ask "<question>"` for one-shot use. Each question is an independent
   turn; the Python example above exercises this lab's background agents.
   `ask` retains Lab 2B's file, test, repository and CLI tools behind the
   same hooks (shell and destructive Git denied; project hooks and rules
   from `.harness/` in the working directory), shows a spinner while it
   works, and ends each answer with the total time and a `Summary:` of
   LLM and tool calls.
   `--repo PATH` changes the tools' starting directory.

## External integrations

The following integration requires learner-provisioned credentials and resources;
this snapshot does not include a command to run it:
- ACA sandbox execution

All live paths must use Entra credentials and must not add API-key configuration.
