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

- ACA code executor

All live paths must use Entra credentials and must not add API-key configuration.
