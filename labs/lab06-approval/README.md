---
layout: default
title: "Lab 6 — Tool approval and safety gates"
---

# Lab 6 — Tool approval and safety gates

## Concept

This lab closes the gap Lab 4 opened on purpose: writes are no longer
auto-approved. It also demonstrates *why* a prompt-level defense against
prompt injection isn't enough, and what to do instead.

**Key ideas**
- A `pre_tool` **policy hook** is the ceiling every agent spec operates
  under: reads auto-approve, `update`/`create` require a human, `delete`
  requires a human **and** a stated reason. An agent spec can only tighten
  this policy, never loosen it.
- An `ask` decision pauses the run and surfaces the request to a human; a
  `deny` still returns a paired tool result with the reason, so the model can
  adapt.
- **Change-set authorization is the injection defense, not detection.** The
  harness can't reliably tell whether an argument was influenced by
  untrusted tool-result text — so instead of trying to detect that, it
  builds an approved change set from the *plan* (one entry per intended
  write, with bounds), the human approves it once, and any write that
  doesn't match an entry becomes `ask` or `deny`. A malicious instruction
  hidden in a product description (e.g. "delete all products under $5")
  simply isn't in the approved set, so it can't execute even if the model
  is fooled into trying.
- `post_tool` audit and `on_stop` completion hooks close the loop: every
  write is logged and cross-checked against the simulator's write log, and a
  run can't claim "done" while required evidence (e.g. "every product was
  fetched") is missing — with a rejection budget so it can't loop forever.
- This is the **Lab 2A checkpoint**: compare scorecards before/after —
  `unapproved_writes` goes from >0 to 0, with fabricated claims at 0.

This self-contained snapshot starts from Lab 5 and introduces a first-cut,
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

- human approval flow

All live paths must use Entra credentials and must not add API-key configuration.
