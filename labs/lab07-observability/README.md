---
layout: default
title: "Lab 7 — Observability and prompt caching"
---

# Lab 7 — Observability and prompt caching

So far each answer ends with a one-line `Summary:`. That tells you *that*
time and tokens were spent, not *where*. This standalone snapshot turns a
run into data: `harness ask --trace FILE` writes every step as one JSON
event per line, and `harness trace FILE` folds the events into a summary,
the way a log pipeline would. `/cost` and `/context` show the same numbers
interactively.

The exercise matches the
[Claude Code Lab 7](../../existing-harnesses/claude-code/lab07-observability/).

## What changes

- [`harness/tracing.py`](harness/tracing.py):
  - `MeteredClient` wraps the model client and measures every call
    (latency, input/output/cached tokens, stop reason, tools requested). It
    never changes the call.
  - `TraceWriter` appends events to a JSONL file: `run_start`,
    `model_call`, `tool_call`, `tool_result` (ok / denied / error and
    size), `denied` and `hook` (hook decisions), `permission` (every
    allow/ask/deny decision and why), `run_end` (totals, any error).
  - Arguments and results are **redacted** (bearer tokens, `api_key`
    fields, `NAME_KEY=value` assignments) and truncated before they are
    written. A trace, like a session file, holds prompts and file contents.
  - `summarize()` is a fold over those events. Cost is an **estimate** from
    prices you supply in USD per million tokens. It is not your Azure bill;
    use Azure Cost Management for actual Foundry spend.
- [`harness/chat.py`](harness/chat.py) records the trace around each
  question and keeps running totals for `/cost`.
- The CLI:
  - `harness ask --trace FILE` appends to `FILE` (one or many runs).
  - `harness trace FILE [--input-price P --output-price P]` prints the
    summary. `HARNESS_PRICE_INPUT` and `HARNESS_PRICE_OUTPUT` in the lab's
    `.env` set default prices.
  - `/cost` shows LLM calls, tokens and estimated cost for this process.
  - `/context` shows what the last request was made of: system prompt
    (including memory files), tool definitions, messages and tool results.

[`harness/telemetry.py`](harness/telemetry.py) keeps the earlier
OpenTelemetry-style span model and the `redact()` the trace uses.

## Learner steps

**Start from:** `labs/app/` at tag `lab06-done` (see the
[track guide](../README.md#working-in-labsapp)).

1. Install this lab and configure Foundry as before. Optionally add your
   model's list prices (USD per million tokens) to the lab's `.env`, for
   example `HARNESS_PRICE_INPUT=3` and `HARNESS_PRICE_OUTPUT=15`:

   ```bash
   python -m venv .venv
   . .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
   pip install -e '.[dev]'
   cp .env.example .env
   az login
   cd ../app
   echo ".runs/" >> .gitignore && git commit -am "chore: ignore traces"
   ```

2. **Capture a run.** A one-shot question with no one to approve edits, so
   allow edits up front (your Lab 6 rules still apply):

   ```bash
   harness ask --accept-edits --trace .runs/lab07.jsonl "Add a 'stats' CLI command that prints product count, total stock units and total inventory value in dollars. Add a test and run the tests. Do not commit."
   ```

3. **Summarize it.**

   ```bash
   harness trace .runs/lab07.jsonl
   ```

   **Observe:** LLM calls and their total time, input/output/cached
   tokens, tool calls by name, tool results (ok / denied / error), hook
   events (your Lab 2B `run_tests.py` feedback), permission decisions,
   duration and the estimated cost. Then open the JSONL and find one
   `tool_call` and its `tool_result`, and the `model_call` that requested
   it. The summary is just a fold over these events.

4. **Interactive views.** Continue the session the run created (one-shot
   runs are sessions too):

   ```bash
   harness ask -c
   ```

   ```text
   How many products have stock below the low-stock threshold?
   ```

   Then type `/cost` and `/context`. **Observe:** in `/context`, how much of
   the request is old tool results compared with the system prompt and tool
   definitions. Compare the input tokens of this question with the first
   question's in the trace: the whole session is resent each time.

5. **Transcripts on disk.** The session itself is the most complete record:

   ```bash
   harness sessions
   ```

   Open the newest `.jsonl` under `~/.harness/projects/`. Treat sessions and
   traces as sensitive: they contain your prompts, file contents and command
   output. The trace redacts and truncates; the session keeps everything.

6. **Record:** LLM calls, tool calls by type, hook events, tokens,
   estimated cost and duration for the step 2 run. Keep this table; Lab 14
   compares against it.

7. **Checkpoint.** Review and commit the `stats` command if the tests pass
   (or `git restore .` and delete untracked files), then in `app/`:

   ```bash
   git tag lab07-done
   ```

8. Back in the lab folder, run the offline checks and inspect the declared
   capabilities:

   ```bash
   pytest checks/
   harness lab-info
   ```

`harness ask` keeps permissions (Lab 6), file memory (Lab 5), plan mode and
todos (Lab 4), sessions (Lab 3) and the Lab 2B tools, built-in policy,
project hooks and rules. This is a teaching harness, not a sandbox: only
use it on the practice app.
