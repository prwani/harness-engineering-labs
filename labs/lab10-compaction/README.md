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

## Learner steps

1. Create and activate a virtual environment, then install the lab:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

2. Force compaction on a long exchange and inspect what stays in context:

   ```bash
   python - <<'PY'
   from harness.compaction import CompactionPolicy, compact

   messages = [{"role": "user", "content": "x" * 200},
               {"role": "assistant", "content": "y" * 200},
               {"role": "user", "content": "Keep this recent question."}]
   kept, handoff = compact(CompactionPolicy(token_threshold=10, keep_recent=1), messages)
   print("Dropped:", handoff.dropped_message_count)
   print("Summary:", kept[0]["content"])
   print("Recent message preserved:", kept[-1] == messages[-1])
   PY
   ```

   The compacted transcript retains a summary and the most recent message.
3. Run `pytest checks/test_compaction.py` for deterministic verification, then
   `pytest checks/` for the full regression suite.
4. Inspect the snapshot's declared capabilities with `harness lab-info`.
5. Optional: to try the live Foundry prompt, copy `.env.example` to `.env`,
   fill in the endpoint and deployment settings, and sign in with `az login`.
   Run `harness ask` to ask repeated questions and type `/exit` to leave; use
   `harness ask "<question>"` for one-shot use. Each question is an independent
   turn; the Python example above exercises this lab's compaction feature.

## External integrations

The following integration requires learner-provisioned credentials and resources;
this snapshot does not include a command to run it:
- long-running Foundry context profile

All live paths must use Entra credentials and must not add API-key configuration.
