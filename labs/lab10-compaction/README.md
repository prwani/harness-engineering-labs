---
layout: default
title: "Lab 10 — Context and compaction"
---

# Lab 10 — Context and compaction

Every question resends the whole session, so a long investigation fills
the context window (Lab 7's `/context` showed how). This standalone
snapshot lets you act on that in `harness ask`: **compact** the history
into a model-written summary, optionally steered by your instructions,
and check which facts survive.

The exercise matches the
[Claude Code Lab 10](../../existing-harnesses/claude-code/lab10-compaction/).
[`make_log.py`](make_log.py) writes a 6,000-line synthetic `app.log` with
a few important facts buried in noise.

## What changes

- `/compact [instructions]`:
  - sends the history to the model with a request to summarize it (your
    instructions are appended), then **replaces** the history with that
    summary. The CLI prints the summary and the token estimates before
    and after.
  - the session file keeps the full record: a `reset` entry marks where
    the compacted history starts, so `-c`/`-r` resume from the summary.
- `/clear` empties the history; files, todos and session approvals stay.
- `harness ask --compact-at TOKENS` compacts automatically **before a
  question** once the previous request reached that many input tokens. It
  doesn't compact in the middle of a run.
- `/context` adds the current history size, so you can see the drop right
  after compacting.
- `read_file` takes optional `start_line` and `max_lines` (up to 1000
  lines per call), so the model can read files over the 100 KB whole-file
  limit in parts. A whole-file read cut at 20,000 characters now says so.
- With `--trace`, each compaction is a `compact` event.

The summary prompt and history rewrite are in
[`harness/compaction.py`](harness/compaction.py), next to the earlier
in-process models of a compaction policy, summary handoff and repository
map.

## Learner steps

**Start from:** `labs/app/` at tag `lab09-done` (see the
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

2. Generate the incident log:

   ```bash
   python ../lab10-compaction/make_log.py
   ```

   `app.log` is ignored by the app's `*.log` rule. Don't open it yet.

3. Investigate:

   ```bash
   harness ask -n incident
   ```

   ```text
   Last night checkout failures spiked. Investigate app.log: find the root cause, the deploy involved, the affected order IDs and region, and when it was fixed. Read the whole log and show your evidence.
   ```

   Then type `/context`.

   **Observe:** the `read_file` calls with `start_line`/`max_lines`, and
   how much of the request the log takes (tool results).

4. Compact with instructions:

   ```text
   /compact Keep: root cause, config key and values, deploy id, affected order IDs and region, rollback time, and the fix plan. Drop raw log lines.
   ```

   Read the printed summary, then type `/context` again. Ask, without
   letting it re-read the log:

   ```text
   Without reading any files, answer: what config changed, from what to what, in which deploy, which orders failed, in which region, and when was it rolled back?
   ```

   **Check against the answer key:** `payment.timeout_ms` changed from
   `5000` to `500` in deploy `7f3a2c`; orders `ORD-2047`, `ORD-2113`,
   `ORD-2190` timed out in `eu-west`; then a rollback followed. The
   "out of stock sku=P3" lines are noise, not the cause.

5. Compare with an unguided compact. `/exit`, start a new session
   (`harness ask -n incident-plain`), repeat step 3, then use plain
   `/compact` and ask the same question. Optionally try `/clear` to see
   what losing everything looks like.

   To see automatic compaction, start one more session with a threshold
   below the size `/context` reported, for example
   `harness ask -n incident-auto --compact-at 30000`, investigate, then
   ask the follow-up question.

6. **Record**

   | | Facts kept (of 6) | `/context` before | after |
   |---|---|---|---|
   | `/compact` with instructions | | | |
   | plain `/compact` | | | |

   Note any hallucinated "facts" after compaction.

7. **Checkpoint.** Nothing to commit (the log is ignored). In `app/`:

   ```bash
   git tag lab10-done
   ```

8. Back in the lab folder, run the offline checks and inspect the declared
   capabilities:

   ```bash
   pytest checks/
   harness lab-info
   ```

`harness ask` keeps subagents and background agents (Lab 9), skills and
MCP (Lab 8), tracing (Lab 7), permissions (Lab 6), file memory (Lab 5),
plan mode and todos (Lab 4), sessions (Lab 3) and the Lab 2B tools,
built-in policy, project hooks and rules. This is a teaching harness, not
a sandbox: only use it on the practice app.
