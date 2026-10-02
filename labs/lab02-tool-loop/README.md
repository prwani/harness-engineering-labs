---
layout: default
title: "Lab 2A — Tool loop and unrestricted CLI tools"
---

# Lab 2A — Tool loop and unrestricted CLI tools

## Concept

This is where the harness stops being a single function call and becomes a
*loop*: the model declares intent ("call this tool with these arguments"),
the harness executes it, and the result is injected back — repeated until the
model stops or an iteration cap is hit. This lab also draws the line the
whole course is built on: the **harness** is the reusable runtime (loop,
tool execution). This first version deliberately exposes unrestricted command
execution so its behavior is easy to observe before later labs add hooks and
policy in Lab 2B.

**Key ideas**
- **Tool-call correlation is an invariant, not a nicety.** Every call gets
  exactly one result and IDs stay paired — Claude groups results into one
  message, GPT addresses them by `call_id`; the harness hides that difference.
- **Tools are host capabilities.** The model can request `git_cli`,
  `azure_cli`, or `shell`, but the harness owns the actual process execution
  and returns the command output to the model.
- **Unsafe by design.** These three tools accept arbitrary commands or
  arguments. This makes the initial demo direct and gives later hook and
  approval labs a concrete unsafe baseline to improve.
- **A hard iteration cap is the first stop condition.** More useful progress
  detection belongs in a later refinement of the loop.
- The repository helpers remain convenient for reads, but they are not a
  security boundary: unrestricted shell commands can read or modify anything
  available to the learner's operating-system account.

This self-contained snapshot starts from Lab 1 and introduces a first-cut,
offline-testable representation of its capability. It retains all earlier checks
and can be installed independently.

## Added in this lab

- [`harness/tool_loop.py`](harness/tool_loop.py) adds `run_tool_loop()`, which
  calls the model, dispatches named tools, pairs results with call IDs, and stops
  on a final turn or the iteration bound.
- [`harness/tools.py`](harness/tools.py) registers repository helpers,
  `write_file` and `edit_file` (exact, unique text replacement), `run_tests`
  (pytest, returning the exit code and output, even on failure), plus
  unrestricted `git_cli`, `azure_cli`, and `shell` tools. That is enough
  for a small coding agent.
- [`harness/learner.py`](harness/learner.py) gives `harness ask` a coding-agent
  system prompt and a 30-iteration budget, because building an app takes many
  model → tool → model rounds.

## Learner steps

**Start from:** `labs/app/` at tag `lab01-done` (see the
[track guide](../README.md#working-in-labsapp)).

**Goal:** watch the loop (model → tool call → result → model …) do real
work. Your harness writes files, runs the tests, reads the failures, fixes
them and uses Git. These are the same exercises as the
[Claude Code Lab 2A](../../existing-harnesses/claude-code/lab02-tool-loop/),
so you can compare the two harnesses later.

> **Warning:** this lab is intentionally unrestricted. The model can run
> any Git, Azure CLI and shell command with your user permissions, and
> nothing asks you first. Work only in `labs/app/`, read every printed
> `Tool:` line, and do not use untrusted prompts or content. Lab 2B adds
> hooks; Lab 6 adds approval.

1. Install this lab and configure the same non-secret Foundry settings used
   in Lab 0, then go to the app:

   ```bash
   python -m venv .venv
   . .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
   pip install -e '.[dev]'
   cp .env.example .env
   az login
   cd ../app
   harness ask
   ```

   Never put credentials or API keys in `.env`. Each question at `You>` is
   a fresh run of the loop: there is no conversation history until Lab 3,
   so every prompt below is self-contained.

2. **Build the app (write + test + fix loop).** Paste this at `You>`:

   ```text
   Build a small Python pet-store order calculator in this folder. Use the standard library only, plus pytest for tests.
   - catalog.csv with header sku,name,price_cents,stock and 5 synthetic products P1..P5 (prices in integer cents)
   - inventory.py: load the catalog into a dict keyed by sku
   - pricing.py: compute an order total in integer cents from (sku, qty) lines, with a tax rate in percent, rounding half up
   - cli.py: `python cli.py total P1:2 P3:1` prints the total like $12.34
   - tests/ with pytest tests for inventory and pricing, including a rounding edge case and a test that loads the real catalog.csv and checks every price and stock is a non-negative integer
   Run the tests with run_tests and fix any failures before you finish.
   ```

   **Observe:** the `Tool: write_file(...)` lines, then `run_tests`, and
   whether a failing `exit_code=1` result is followed by `edit_file` and
   another `run_tests`. That retry *is* the loop: the harness only passes
   results back, and the model decides what to do next. The `Summary:`
   line shows how many LLM and tool calls it took.

3. **Use Git as a tool.** Ask these one at a time (each is a separate run):

   ```text
   Use git to show which files are untracked or changed.
   ```

   ```text
   Commit all app files with a descriptive conventional-commit message.
   ```

   ```text
   Create a branch called feature/low-stock. On it, add a `python cli.py low-stock` command that lists products with stock below 5, with a test. Run the tests, commit, switch back to main, and merge feature/low-stock.
   ```

   **Observe:** `git_cli` calls such as `["status"]`, `["add", "."]`,
   `["switch", "-c", ...]` and `["merge", ...]`. Nothing asked for your
   approval. Check the result in a second terminal with
   `git log --oneline --graph`.

4. **Debug a regression with Git history.** Leave the prompt (`/exit`).
   Now *you* introduce a regression, with a misleading commit message:

   ```bash
   sed -i.bak -E 's/^P2,([^,]+),[0-9]+,/P2,\1,12.99,/' catalog.csv && rm catalog.csv.bak
   git commit -am "docs: tidy catalog formatting"
   ```

   ```powershell
   (Get-Content catalog.csv) -replace '^P2,([^,]+),\d+,', 'P2,$1,12.99,' | Set-Content catalog.csv
   git commit -am "docs: tidy catalog formatting"
   ```

   Then ask:

   ```text
   The tests are failing on main. Use the git history to find which commit broke them and explain why, then fix it in a new commit. Do not rewrite history.
   ```

   **Observe:** does it run the tests first, then `git log`/`show`/`diff`
   to find the commit, instead of guessing? Does it trust the diff rather
   than the misleading "docs:" message? Did it use `shell` for anything
   that a dedicated tool could have done?

5. **Record**
   - How many LLM and tool calls each step took (the `Summary:` lines).
   - Whether a test failure ever led to a fix without your prompting.
   - One tool call you would *not* have allowed if you had been asked.
     Lab 2B turns that into a hook.

6. **Checkpoint.** In `app/`:

   ```bash
   python -m pytest -q
   git status            # should be clean
   git tag lab02a-done
   ```

   Your app will differ from other learners' apps. That is fine, as long
   as the tests pass and `catalog.csv`, `pricing.py`, `inventory.py`,
   `cli.py` and `tests/` exist, because later labs use those names.

7. Back in the lab folder, run `pytest checks/` for the offline regression
   suite (no live model call) and `harness lab-info` to see the declared
   capabilities.

While the harness works, `harness ask` shows a spinner with the elapsed time
on stderr (plain `... waiting for model (LLM call N)` lines when output is
redirected). Each answer ends with the total time next to the token counts and
a summary such as
`Summary: llm_calls=9, tool_calls=14, tool_errors=0, model_time=41.2s, tool_time=2.3s`.
Model calls usually dominate; every tool batch costs another LLM call. The
current directory is used by default; `--repo PATH` selects another one.

Continue with [Lab 2B](../lab02b-hooks/README.md) to add hooks that deny
unsafe commands before they run, project hooks that block edits and run
tests, and scoped rules. Then compare the results with this unrestricted
baseline.

## External integrations

The direct interactive tool-loop exercise above requires a learner-provisioned
Foundry model. This snapshot does not include the automated evaluation suite:
- Foundry tool-call transcript

All live paths must use Entra credentials and must not add API-key configuration.
