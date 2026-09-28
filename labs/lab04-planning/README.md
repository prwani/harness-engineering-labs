---
layout: default
title: "Lab 4 — Planning and todos"
---

# Lab 4 — Planning and todos

## Concept

Up to now the agent has decided each next step greedily, one tool call at a
time. This lab separates **deciding what to do** from **doing it**, as two
agent specs sharing one harness: a `planner` (read-only tools plus
`write_todos`) and a `catalog-fixer` (write tools, works the plan). This
matters because this is also the lab where **write tools appear** —
`update_product`, `create_product`, and the irreversible `delete_product` —
and, deliberately, they are auto-approved for now. That gap is the whole
point of Lab 6.

**Key ideas**
- Todos are a first-class harness primitive, not a prompt convention: the
  harness owns the todo state and re-injects open todos every turn via a
  `pre_model` hook, so the agent can't "forget" the plan.
- Only the harness switches modes; an agent spec can't grant itself write
  tools it wasn't given.
- Plan-then-execute is compared directly against a greedy single-agent
  variant on the same task — expect fewer wasted/wrong writes and higher
  todo completion with planning.
- **Safe resume now covers writes:** every write carries an idempotency key,
  mutating calls run one at a time, and a crash between "applied" and
  "persisted" is reconciled against the simulator's write log on resume — no
  duplicate writes, ever.
- `unapproved_writes > 0` is *expected* here — it's the baseline number Lab 6
  drives to zero.

This self-contained snapshot starts from Lab 3 and introduces a first-cut,
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

- Foundry catalog remediation

All live paths must use Entra credentials and must not add API-key configuration.
