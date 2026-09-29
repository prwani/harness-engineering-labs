---
layout: default
title: "Lab 14 — Native harness comparison"
---

# Lab 14 — Native harness comparison

## Concept

Labs 0–13 built a harness from scratch to show exactly what one does. This
lab proves the point from the other direction: Claude Code and Copilot CLI
**are** harnesses too, and the same agent, the same skill, and the same
mental model port onto them almost unchanged — because they're built out of
the same layers.

**Key ideas**
- `agents/catalog-fixer.md` is ported to each tool's native custom-agent
  format; the `skills/product-description/` folder mounts **unchanged**;
  store tools are exposed through a small MCP server wrapping the same
  simulator used since Lab 8 — nothing about the *capability* changes, only
  its host.
- Both harnesses authenticate through Entra ID (`az login`), matching this
  course's no-API-keys rule throughout.
- Every custom harness feature has a native counterpart to map onto: the
  approval policy → permission settings/hooks; `pre_tool`/`post_tool`/`on_stop`
  → each tool's own hook types (the Lab 6 change-set check and Lab 7
  redaction hook are ported as real hook scripts); todos/plan mode → plan
  mode; spawning → sub-agents/workflows; compaction → automatic compaction;
  tracing → OTel export or usage commands.
- The same M1 scorecard (accuracy, safety, tokens) is collected here as in
  every earlier lab, so the comparison is apples-to-apples: what did the
  commercial harness give for free, and what could you *not* control — the
  transcript, the compaction policy, per-call usage?

This self-contained snapshot starts from Lab 13 and introduces a first-cut,
offline-testable representation of its capability. It retains all earlier checks
and can be installed independently.

## Added in this lab

- [`harness/native_harness.py`](harness/native_harness.py) adds
  `ComparisonScorecard` / `ScorecardEntry` for comparing run metrics and
  `render_comparison()` for tabular results.
- The same module adds `LAYER_MAPPING`, `claude_code_mapping()`, and
  `copilot_cli_mapping()` as reference mappings to native harness concepts.

## Learner steps

1. Create and activate a virtual environment, then install the lab:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

2. Run the focused test for this lab's native-harness comparison behavior:
   `pytest checks/test_native_harness.py`. It uses deterministic fixtures, so it runs offline.
3. Run all checks for this snapshot and earlier labs: `pytest checks/`.
4. Inspect the snapshot's declared capabilities: `harness lab-info`.

## External integrations

The following integration requires learner-provisioned credentials and resources;
this snapshot does not include a command to run it:
- Claude Code and Copilot CLI runs

All live paths must use Entra credentials and must not add API-key configuration.
