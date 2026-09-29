---
layout: default
title: "Lab 2 — Tool loop and agent spec"
---

# Lab 2 — Tool loop and agent spec

## Concept

This is where the harness stops being a single function call and becomes a
*loop*: the model declares intent ("call this tool with these arguments"),
the harness executes it, and the result is injected back — repeated until the
model stops or an iteration cap is hit. This lab also draws the line the
whole course is built on: the **harness** is the reusable runtime (loop,
tool execution, hooks), and the **agent spec** is per-job configuration
(instructions, tool allow-list, model). The same harness will host many
different agents in later labs.

**Key ideas**
- **Tool-call correlation is an invariant, not a nicety.** Every call gets
  exactly one result, IDs stay paired, and `history.validate()` runs before
  every model call — Claude groups results into one message, GPT addresses
  them by `call_id`; the harness hides that difference.
- **Hooks, not more loop code.** `pre_tool` validates arguments and sandbox
  paths; `pre_model` validates history. Every later lab's cross-cutting
  behavior (approval, redaction, caching, compaction) is added the same way.
- **The agent spec is the seam.** Moving the system prompt, tool list, and
  model choice into `agents/store-ops.md` means swapping Claude for GPT is a
  one-line config change, not a code change.
- **Progress detection beyond a raw iteration cap:** duplicate-call
  suppression, a per-turn output budget, and stall detection (no *new*
  information served for 3 turns) stop a run that's spinning without
  actually running out of turns.
- With write tools still absent, accuracy on "diagnose" rises sharply over
  Lab 1's bare call — but "fix" stays at zero. That gap is next.

This self-contained snapshot starts from Lab 1 and introduces a first-cut,
offline-testable representation of its capability. It retains all earlier checks
and can be installed independently.

## Added in this lab

- [`harness/tool_loop.py`](harness/tool_loop.py) adds `run_tool_loop()`, which
  calls the model, dispatches named tools, pairs results with call IDs, and stops
  on a final turn or the iteration bound.

## Learner steps

1. Create and activate a virtual environment, then install the lab:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

2. Run the focused test for this lab's tool-loop behavior: `pytest checks/test_tool_loop.py`.
   It uses deterministic fixtures, so it runs offline.
3. Run all checks for this snapshot and earlier labs: `pytest checks/`.
4. Inspect the snapshot's declared capabilities: `harness lab-info`.

## External integrations

The following integration requires learner-provisioned credentials and resources;
this snapshot does not include a command to run it:
- Foundry tool-call transcript

All live paths must use Entra credentials and must not add API-key configuration.
