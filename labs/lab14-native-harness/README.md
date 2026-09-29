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

2. Inspect how the harness maps to native Claude Code and Copilot CLI concepts:

   ```bash
   python - <<'PY'
   from harness.native_harness import claude_code_mapping, copilot_cli_mapping

   for layer, concept in claude_code_mapping().items():
       print(f"{layer}: Claude Code → {concept}")
       print(f"  Copilot CLI → {copilot_cli_mapping()[layer]}")
   PY
   ```

   Compare each pair and note which capabilities are provided by the native
   harness versus defined in an agent or skill.
3. Run `pytest checks/test_native_harness.py` for deterministic verification,
   then `pytest checks/` for the full regression suite.
4. Inspect the snapshot's declared capabilities with `harness lab-info`.
5. Optional: to try the live Foundry prompt, copy `.env.example` to `.env`,
   fill in the endpoint and deployment settings, and sign in with `az login`.
   Run `harness ask` to ask repeated questions and type `/exit` to leave; use
   `harness ask "<question>"` for one-shot use. Each question is an independent
   turn; the Python example above exercises this lab's native-harness mapping.
   `ask` retains Lab 2B's repository and CLI tools behind the same
   `pre_tool`/`pre_model` hooks (shell denied; Git and Azure CLI limited to
   a few read commands), shows a spinner while it works, and ends each
   answer with the total time and a `Summary:` of LLM and tool calls.
   `--repo PATH` changes the tools' starting directory.

## External integrations

The following integration requires learner-provisioned credentials and resources;
this snapshot does not include a command to run it:
- Claude Code and Copilot CLI runs

All live paths must use Entra credentials and must not add API-key configuration.
