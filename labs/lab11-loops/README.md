---
layout: default
title: "Lab 11 — Loops with a stop condition"
---

# Lab 11 — Loops with a stop condition

Make "done" something the harness checks, not something the model claims.
This standalone snapshot adds **stop hooks** to `harness ask`: a command
that runs when the model gives its final answer and can send it back to
work. You add a failing test (the spec), then compare three loops:

1. **Prompted loop**: the model is asked to keep going until tests pass.
2. **Stop hook**: [`stop_gate.py`](assets/.harness/hooks/stop_gate.py)
   runs pytest whenever the model tries to finish and sends it back while
   tests fail. The harness stops forcing it after 3 blocks, so it can't
   loop forever.
3. **Script loop**: an outer loop you own, bounded and checked by plain
   code.

The exercise matches the
[Claude Code Lab 11](../../existing-harnesses/claude-code/lab11-loops/).

## What changes

- `.harness/settings.json` accepts `stop` hooks:
  `{"command": [...]}` entries, run with the event as JSON on stdin
  (`last_message`, `stop_hook_active`, `cwd`).
  - exit code 2: stderr goes back to the model as a user message ("You are
    not done…") and the loop continues.
  - any other exit code: the answer stands.
- The tool loop owns the bound: at most 3 stop-hook blocks per question;
  after that the answer is returned as is. The summary line shows
  `stop_blocks=N`, and traces record it in `run_end`.
- `harness ask --max-iterations N` caps model calls per question
  (default 30), including the retries a stop hook causes.
- Stop hooks gate the main conversation only. They don't run in plan mode
  (nothing can change) or for subagents.

[`harness/loops.py`](harness/loops.py) keeps the earlier in-process models
of retry, validation, polling and refinement loops.

## Learner steps

**Start from:** `labs/app/` at tag `lab10-done` (see the
[track guide](../README.md#working-in-labsapp)).

The spec,
[`assets/tests/test_bulk_discount.py`](assets/tests/test_bulk_discount.py):
`pricing.bulk_discount_percent(qty)` returns 0 below 10, 5 for 10–49, 10
for 50 or more, and raises `ValueError` for qty ≤ 0. The new settings deny
edits to that test file, so the model can't "pass" by changing the spec.

1. Install this lab and configure Foundry as before:

   ```bash
   python -m venv .venv
   . .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
   pip install -e '.[dev]'
   cp .env.example .env
   az login
   cd ../app
   ```

2. Add the spec (red):

   ```bash
   git switch -c feature/bulk-discount
   cp ../lab11-loops/assets/tests/test_bulk_discount.py tests/
   python -m pytest -q          # should fail
   git add tests && git commit -m "test: bulk discount spec"
   ```

3. Prompted loop (no gate):

   ```bash
   harness ask --accept-edits --max-iterations 15 "Implement pricing.bulk_discount_percent so tests/test_bulk_discount.py passes. Keep running the tests and fixing until they all pass."
   python -m pytest -q
   git stash -u      # set the attempt aside to compare later
   ```

   It usually works for a task this small. The question is *who*
   verified it: only the model.

4. Stop-hook gate. Install the Lab 11 settings and hook (they keep the
   Lab 6 permissions and Lab 2B hooks, and add the spec protection and the
   `stop` hook), then ask without mentioning tests:

   ```bash
   cp -R ../lab11-loops/assets/.harness .
   harness ask --accept-edits --max-iterations 15 --trace .runs/lab11-stop.jsonl "Implement pricing.bulk_discount_percent. Be brief."
   harness trace .runs/lab11-stop.jsonl
   ```

   ```powershell
   Copy-Item -Recurse -Force ..\lab11-loops\assets\.harness .
   harness ask --accept-edits --max-iterations 15 --trace .runs\lab11-stop.jsonl "Implement pricing.bulk_discount_percent. Be brief."
   harness trace .runs\lab11-stop.jsonl
   ```

   **Observe:** if the model stops early, `Hook: stop: stop_gate.py:
   pytest is failing…` and another round of tool calls; the summary line
   shows `stop_blocks`. `--max-iterations` is a second, harder bound.

5. Script loop (you own the loop):

   ```bash
   git restore pricing.py     # start from red again; keep the Lab 11 settings
   for i in 1 2 3; do
     python -m pytest -q tests/test_bulk_discount.py && { echo "green after $((i-1)) attempt(s)"; break; }
     harness ask --accept-edits --max-iterations 8 "Tests in tests/test_bulk_discount.py fail. Make one focused change to pricing.py to fix them."
   done
   ```

   ```powershell
   git restore pricing.py
   for ($i = 1; $i -le 3; $i++) {
       python -m pytest -q tests/test_bulk_discount.py
       if ($LASTEXITCODE -eq 0) { Write-Host "green after $($i-1) attempt(s)"; break }
       harness ask --accept-edits --max-iterations 8 "Tests in tests/test_bulk_discount.py fail. Make one focused change to pricing.py to fix them."
   }
   ```

   Here the stop condition, bound and verification are ordinary code; each
   iteration is a new session with no memory of the last one. (The stop
   hook still runs inside each attempt; remove the `stop` entry from
   `.harness/settings.json` to see the script loop alone.)

6. **Record**

   | Loop | Who checks "done"? | Bound | Iterations / LLM calls | Cost |
   |---|---|---|---|---|

7. **Checkpoint.** Keep the best implementation (drop the stash with
   `git stash drop`), commit, merge:

   ```bash
   python -m pytest -q
   git add .harness pricing.py && git commit -m "feat: bulk discount with stop-hook gate"
   git switch main && git merge --no-ff feature/bulk-discount
   git tag lab11-done
   ```

8. Back in the lab folder, run the offline checks and inspect the declared
   capabilities:

   ```bash
   pytest checks/
   harness lab-info
   ```

`harness ask` keeps compaction (Lab 10), subagents and background agents
(Lab 9), skills and MCP (Lab 8), tracing (Lab 7), permissions (Lab 6),
file memory (Lab 5), plan mode and todos (Lab 4), sessions (Lab 3) and the
Lab 2B tools, built-in policy, project hooks and rules. This is a teaching
harness, not a sandbox: only use it on the practice app.
