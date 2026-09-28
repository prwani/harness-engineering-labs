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

- ACA sandbox execution

All live paths must use Entra credentials and must not add API-key configuration.
