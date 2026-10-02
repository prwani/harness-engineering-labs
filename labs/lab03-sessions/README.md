---
layout: default
title: "Lab 3 — History and sessions"
---

# Lab 3 — History and sessions

Until now every question at `You>` was a fresh run: the model forgot the
previous answer as soon as it was printed. This standalone snapshot gives
`harness ask` a **session**: the conversation (your questions, the model's
turns, every tool call and its result) is kept between questions and
appended to a JSONL file after every step. You can leave, come back and
**continue**, **resume** a named session, or **fork** it to try an
alternative without touching the original.

A session is the conversation, **not** a snapshot of your files. In this lab
you change the repository while the harness isn't looking and see what a
restored conversation does and doesn't know. The exercise matches the
[Claude Code Lab 3](../../existing-harnesses/claude-code/lab03-sessions/).

## What changes

- [`harness/tool_loop.py`](harness/tool_loop.py) accepts the conversation
  so far (`history`) and appends the new question, each model turn, each
  tool result and the final answer to it. `on_message` sees every appended
  message, which is how the session saves it.
- [`harness/session.py`](harness/session.py):
  - `SessionStore` keeps a project's sessions under
    `~/.harness/projects/<project-path>/sessions/` (set `HARNESS_HOME` to
    move it), outside your repository, like Claude Code's `~/.claude`.
    Each session is `<id>.jsonl` (one line per message) plus
    `<id>.meta.json` (name, creation time, the session it was forked from).
  - `open()` starts a new session or continues the latest, resumes one by
    ID, ID prefix or name, and optionally forks it into a new copy.
  - `repair_history()` handles a crash in the middle of a tool call. A call
    with no saved result gets an explicit "interrupted" result, so the
    model checks the current state instead of the call being silently
    dropped or blindly re-run.
- [`harness/hooks.py`](harness/hooks.py): `validate_history` now checks a
  conversation of many questions. Every assistant turn with tool calls must
  still be followed by exactly one result per call.
- The CLI:
  - `harness ask` options `-n/--name NAME`, `-c/--continue`,
    `-r/--resume ID|NAME` and `--fork`. It prints the session it opened.
  - `harness sessions` lists the project's sessions (size, message count,
    first question, fork origin).
  - At `You>`, `/session` shows the session file and `/history` lists the
    questions so far.

## Learner steps

**Start from:** `labs/app/` at tag `lab02b-done` (see the
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

2. **Start a named session and investigate.**

   ```bash
   harness ask -n low-stock-threshold
   ```

   ```text
   The low-stock threshold is hardcoded. Investigate how it's used and write NOTES.md with a short plan to make it configurable (CLI flag and/or environment variable). Don't change any code yet.
   ```

   Leave with `/exit`, then list the project's sessions:

   ```bash
   harness sessions
   ```

   **Observe:** the session file location, its size and message count. Open
   the `.jsonl` file: every tool call and result is there, including the
   full text of each file the model read.

3. **Change the repo while the harness isn't looking.** In the same
   terminal, act as a teammate. The `protect_catalog.py` hook only stops
   the agent; you can still edit the file:

   ```bash
   git add NOTES.md && git commit -m "docs: threshold notes"
   sed -i.bak -E 's/^(P4,[^,]+,[0-9]+),[0-9]+$/\1,2/' catalog.csv && rm catalog.csv.bak
   git commit -am "chore: restock data from warehouse sync"
   ```

   ```powershell
   git add NOTES.md ; git commit -m "docs: threshold notes"
   (Get-Content catalog.csv) -replace '^(P4,[^,]+,\d+),\d+$', '${1},2' | Set-Content catalog.csv
   git commit -am "chore: restock data from warehouse sync"
   ```

4. **Continue the most recent session.**

   ```bash
   harness ask -c
   ```

   ```text
   Continue: implement the plan from NOTES.md, with tests. Before you start, tell me which products are currently low on stock.
   ```

   **Observe:** the opening line shows the restored message count, and the
   model remembers the plan without re-reading everything. But does it
   trust its *memory* of `catalog.csv` (still in the history as an old tool
   result) or call `read_file` again? Is P4 (stock now 2) in its list? A
   restored session can hold stale facts about files that changed since.
   When the feature is done and the tests pass, ask it to commit, then
   `/exit`.

5. **Resume by name, then fork an alternative.**

   ```bash
   harness ask -r low-stock-threshold
   ```

   Type `/history` to see the questions so far, then `/exit`. Now **fork**
   that conversation, so you can try a different design without adding to
   the original history:

   ```bash
   git switch -c try/env-only
   harness ask -r low-stock-threshold --fork
   ```

   ```text
   Alternative design: drop the CLI flag and support only an environment variable LOW_STOCK_THRESHOLD. Implement it, run the tests and commit.
   ```

   `/exit`, then run `harness sessions`: the original and the fork are
   separate entries, and the fork says which session it came from. Decide
   which design you prefer, then switch back and delete the branch you're
   not keeping:

   ```bash
   git switch main && git branch -D try/env-only
   ```

6. **Record**
   - What `-c` restored, and whether stale file knowledge caused a mistake.
   - How `-c`, `-r` and `--fork` differ, and what `-n` adds.
   - Where the session files live and roughly how big they are. They hold
     your prompts and file contents, so treat them as sensitive.

7. **Checkpoint.** In `app/`:

   ```bash
   git switch main && python -m pytest -q
   git tag lab03-done
   ```

8. Back in the lab folder, run the offline checks and inspect the declared
   capabilities:

   ```bash
   pytest checks/
   harness lab-info
   ```

**Cost note:** each question resends the whole session, including old tool
results, so input tokens grow with every question. Compare the `Tokens:`
line of the first and last questions in step 4. Lab 10 (compaction)
addresses this growth.

`harness ask` keeps the Lab 2B tools, built-in policy, project hooks and
rules, and ends each answer with the elapsed time and a `Summary:` line.
`--repo PATH` selects another project; its sessions are stored separately.
This is a teaching harness, not a sandbox: only use it on the practice app.
