---
layout: default
title: "Lab 10 — Compaction and repository map"
---

# Lab 10 — Compaction and repository map

## Concept

Lab 3 flagged that resending the whole history every turn makes context grow
without bound; Lab 7's traces made that growth visible as a token curve. This
lab is where the harness finally *acts* on it: a `pre_model` hook rewrites
history down to a smaller footprint while preserving what actually matters.

**Key ideas**
- Compaction is trigger-and-target driven (e.g. compact at 80% of budget
  down to 35%), not "compact every turn" — using one value for both makes it
  fire on nearly every turn and is a documented anti-pattern.
- A **minimum-saving threshold** skips compaction that wouldn't free enough
  context to be worth invalidating the cache for.
- **What survives vs. what compresses:** the active plan, todos, task state,
  files-already-read list, and repo map are kept; raw tool output and
  resolved exchanges are compressed into a fixed-schema summary (checked
  against a JSON Schema, so nothing silently disappears).
- **A tool call and its result are atomic.** Naive tail truncation can orphan
  one half of a pair and produce a 400 from either provider —
  `history.validate()` (Lab 2) is what catches this.
- Compaction **invalidates the cached prefix** after the last stable
  breakpoint, so it has a real cost too; the context profile changes shape
  from a ramp (Lab 9's flat per-agent profile) to a sawtooth.

This self-contained snapshot starts from Lab 9 and introduces a first-cut,
offline-testable representation of its capability. It retains all earlier checks
and can be installed independently.

## Added in this lab

- [`harness/compaction.py`](harness/compaction.py) adds `CompactionPolicy`,
  `compact()`, and `SummaryHandoff` to replace older messages with a summary
  while retaining recent messages.
- The same module adds `build_repo_map()` for a stable index of files and
  directories.

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

- long-running Foundry context profile

All live paths must use Entra credentials and must not add API-key configuration.
