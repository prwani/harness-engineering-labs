---
layout: default
title: "Lab 14 — Cross-harness comparison"
---

# Lab 14 — Cross-harness comparison

Run the **same task** under the same conditions in the harness you built,
in Claude Code and/or another harness (the
[Codex CLI track](../../existing-harnesses/codex-cli/)), then compare
with measured numbers rather than impressions.

The exercise matches the
[Claude Code Lab 14](../../existing-harnesses/claude-code/lab14-comparison/).

## What changes

- `harness features` prints each capability you built in Labs 2–13, the
  command or file that drives it here, and its Claude Code counterpart.
  Use it for the qualitative part of the comparison.
- Nothing else: `harness ask --trace` and `harness trace` (Lab 7) already
  measure a run.

[`harness/native_harness.py`](harness/native_harness.py) holds the feature
map, next to the earlier comparison scorecard schema and layer mappings.

## Learner steps

**Start from:** `labs/app/` at tag `lab13-done` (see the
[track guide](../README.md#working-in-labsapp)).

1. Install this lab and configure Foundry as before:

   ```bash
   python -m venv .venv
   . .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
   pip install -e '.[dev]'
   cp .env.example .env
   az login
   cd ../app
   ```

2. Fix the task and the conditions. Use one well-specified task with an
   objective check:

   ```text
   Add a `python cli.py export --format json` command that prints the catalog as a JSON array of objects with integer price_cents and stock. Add tests. Run the full test suite and stop only when it passes. Do not commit.
   ```

   Keep these identical across harnesses, and write them down: starting
   commit (`lab13-done`), model/deployment, instruction files
   (`HARNESS.md`/`CLAUDE.md`/`AGENTS.md` with the same content),
   permissions (edits auto-accepted, tests allowed, no network, no push),
   hooks (the Lab 11 stop gate is in `.harness/settings.json`; install the
   equivalent elsewhere or remove it everywhere) and a turn or budget
   limit. Set `HARNESS_PRICE_INPUT`/`HARNESS_PRICE_OUTPUT` in this lab's
   `.env` to the list prices of your deployment.

3. Run it in your harness:

   ```bash
   task='Add a `python cli.py export --format json` command that prints the catalog as a JSON array of objects with integer price_cents and stock. Add tests. Run the full test suite and stop only when it passes. Do not commit.'
   git switch -c compare/harness lab13-done
   harness ask --accept-edits --max-iterations 30 --trace .runs/lab14-harness.jsonl "$task"
   python -m pytest -q
   harness trace .runs/lab14-harness.jsonl
   git diff --stat lab13-done
   ```

   ```powershell
   $task = 'Add a `python cli.py export --format json` command that prints the catalog as a JSON array of objects with integer price_cents and stock. Add tests. Run the full test suite and stop only when it passes. Do not commit.'
   git switch -c compare/harness lab13-done
   harness ask --accept-edits --max-iterations 30 --trace .runs\lab14-harness.jsonl $task
   python -m pytest -q
   harness trace .runs\lab14-harness.jsonl
   git diff --stat lab13-done
   ```

   Repeat once or twice if you can (append to the same trace, or use a new
   file per run); one run is an anecdote.

4. Run it elsewhere. Commit the previous run's changes on its own branch
   (or discard them) so they don't follow you, then check out a fresh
   branch from `lab13-done` for each other harness
   (`git switch -c compare/claude lab13-done`), run the same prompt with
   that harness's equivalent headless and permission settings (see
   [Claude Code Lab 14](../../existing-harnesses/claude-code/lab14-comparison/)),
   and capture its own event log or usage output.

5. Compare:

   | Metric | This harness | Other harness | How measured |
   |---|---|---|---|
   | Tests pass at the end | | | `python -m pytest -q` |
   | Files changed / lines | | | `git diff --stat lab13-done` |
   | LLM calls | | | `harness trace` / event stream |
   | Tool calls (by type) | | | `harness trace` / event stream |
   | Input / output tokens | | | `harness trace` / event stream |
   | Cost estimate | | | list price × tokens |
   | Wall-clock time | | | `harness trace` duration / stopwatch |
   | Policy violations | | | denials, hooks, manual review |

   And qualitatively, with `harness features` beside you: which
   capabilities were **built in**, **configured** (settings, hooks,
   skills), **orchestrated by you** (Labs 11–13) or **unavailable** in each
   harness? Which ones could you change in your own harness that you
   couldn't elsewhere (the transcript, the compaction prompt, the loop
   bound)?

6. **Caveats**
   - Only compare numbers produced under matching conditions. Cost
     figures are estimates from token counts and list prices, not your
     Azure bill.
   - Your harness's system prompt and tool set are much smaller than a
     commercial harness's; a lower token count isn't automatically better
     if the task isn't done.
   - Don't report scores you didn't observe.

7. **Checkpoint.** Keep the branch whose result you prefer (or none),
   switch back to `main`:

   ```bash
   git switch main
   git tag lab14-done
   ```

8. Back in the lab folder, run the offline checks and inspect the declared
   capabilities:

   ```bash
   pytest checks/
   harness lab-info
   ```

This snapshot contains every capability from Labs 2–13. This is a teaching
harness, not a sandbox: only use it on the practice app.
