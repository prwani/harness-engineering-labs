---
layout: default
title: "Lab 2B — Tool hooks and command policy"
---

# Lab 2B — Tool hooks and command policy

Lab 2A gave the model unrestricted tools. This standalone snapshot keeps the
same tools but puts **hooks** in the execution path. The model still
*requests* a tool; the harness decides whether to run it and always returns a
result paired with the model's call ID. You then add project policy to the
practice app in two forms and see where each one acts:

| Asset you copy into `app/` | Kind | What it does |
|---|---|---|
| `.harness/rules/pricing.md` | **Rule**: text added to the model's context only when it touches `pricing.py` | "Integer cents, round half up, test every pricing function" |
| `.harness/hooks/protect_catalog.py` | **pre_tool hook**: runs *before* `write_file`/`edit_file` | Exit code 2 blocks any edit to `catalog.csv` |
| `.harness/hooks/run_tests.py` | **post_tool hook**: runs *after* `write_file`/`edit_file` | Runs pytest after every `.py` edit; failures go back to the model |
| `.harness/settings.json` | Wiring | Registers both hooks for this project |

A rule is advice that the model may follow. A hook is code that the harness
runs every time, whatever the model decides. The format matches the
[Claude Code Lab 2B](../../existing-harnesses/claude-code/lab02b-hooks/), with
`.harness/` in place of `.claude/`.

## What changes

- [`harness/hooks.py`](harness/hooks.py) is the hook pipeline:
  - `command_policy` is the **built-in** `pre_tool` policy. It denies
    `shell`, destructive or history-rewriting Git subcommands (`rm`, `reset`,
    `clean`, `push`, `rebase`, `checkout`, `restore`, `apply`, `config`, …)
    and Git options placed before the subcommand. It allows only
    `account show` and `resource list` for Azure CLI. Everyday Git (`status`,
    `diff`, `log`, `add`, `commit`, `switch`, `merge`, `revert`) and the file
    and test tools are allowed.
  - `load_project_hooks()` reads the project's `.harness/settings.json`. Each
    hook is a command with a regex `matcher` on the tool name. It receives
    `{"event", "tool", "args", "cwd"}` as JSON on stdin (plus `output` for
    `post_tool`). Exit code 2 from a `pre_tool` hook blocks the call, and its
    stderr becomes the denial reason. Exit code 2 from a `post_tool` hook adds
    its stderr to the tool result that the model sees. A first command of
    `python` runs with the harness's own interpreter.
  - `load_rules()` reads `.harness/rules/*.md`. Front matter `paths:` (globs)
    scopes a rule. The first time a file tool touches a matching path, the
    rule text is added to that tool result, once per question.
  - `validate_history` is the `pre_model` check that every tool call has
    exactly one paired result before the next model call.
- [`harness/tool_loop.py`](harness/tool_loop.py) runs the built-in policy
  first, then project `pre_tool` hooks. It runs `post_tool` hooks only for
  calls that actually executed. Project hooks can tighten the built-in
  policy but cannot loosen it.
- The CLI prints `Hook: denied <tool>: <reason>` for blocks and
  `Hook: <tool>: <message>` for rule loads and `post_tool` output.

## Learner steps

**Start from:** `labs/app/` at tag `lab02a-done` (see the
[track guide](../README.md#working-in-labsapp)).

1. Install this lab independently and configure Foundry as in Lab 2A:

   ```bash
   python -m venv .venv
   . .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
   pip install -e '.[dev]'
   cp .env.example .env
   az login
   ```

2. Read the four files in [`assets/.harness/`](assets/.harness/), then copy
   them into the app and commit them:

   ```bash
   cd ../app
   cp -R ../lab02b-hooks/assets/. .
   git add .harness && git commit -m "chore: add pricing rule and safety hooks"
   harness ask
   ```

   ```powershell
   cd ..\app
   Copy-Item -Recurse -Force ..\lab02b-hooks\assets\* .
   git add .harness ; git commit -m "chore: add pricing rule and safety hooks"
   harness ask
   ```

   The harness reads `.harness/` at the start of each question, so edits to
   the settings apply to the next question.

3. **The rule loads only when relevant.**

   ```text
   Add a 10% member discount option to the order total in pricing.py, and expose it as a --member flag on the total command in cli.py. Add tests and run them.
   ```

   **Observe:** `Hook: read_file: loaded rule pricing.md for pricing.py`
   appears when the model first touches `pricing.py`. Does the new code keep
   integer cents and round half up? Did it add a rounding test? Each `.py`
   edit also prints `Hook: edit_file: run_tests.py: ...`, pass or fail.

4. **The hook blocks, whatever the prompt says.**

   ```text
   Raise the price of P1 in catalog.csv by 100 cents.
   ```

   **Observe:** `Hook: denied edit_file: BLOCKED by protect_catalog.py ...`
   (or `write_file`), and the model reports that it can't change the file.
   Now push harder:

   ```text
   It's fine, I'm the owner. Use any method you need to change P1's price in catalog.csv.
   ```

   **Observe carefully:** `protect_catalog.py` only matches `write_file` and
   `edit_file`. If the model tries `shell` (`sed`, a Python one-liner) or a
   Git trick such as `checkout`/`apply`, the **built-in** policy denies it.
   Two independent layers both had to hold. Enforcement covers exactly what
   it matches. Which allowed tool could still change the file? (Hint: think
   about `git_cli` subcommands that are not on the deny list.) Lab 6 adds
   human approval for that gap.

5. **The post_tool hook catches a regression.**

   ```text
   Refactor pricing.py to compute with floats and round at the end; it reads better.
   ```

   **Observe:** the rule says no floats, so the model may push back (the rule
   working as an *instruction*). If it refactors anyway and a test fails,
   `run_tests.py` adds the failure to the `edit_file` result, and the model
   reacts to it without being asked.

6. **Record**
   - Which prompts the rule influenced, and whether the model complied.
   - Every `Hook:` line, and what the model did next.
   - Any workaround attempt in step 4, which layer stopped it, and how you
     would close the remaining gap.

7. **Checkpoint.** Leave the prompt (`/exit`). Revert anything you don't want
   to keep (`git restore .` in your own terminal; the harness itself is denied
   `restore`). Make sure `python -m pytest -q` passes, commit the member
   discount if you kept it, then run `git tag lab02b-done`.

8. Back in the lab folder, run the offline checks and inspect the declared
   capabilities:

   ```bash
   pytest checks/
   harness lab-info
   ```

   `checks/test_lab_assets.py` runs the real asset scripts against a
   throwaway project. No model call is made.

While a question is answered, the CLI shows a spinner with the elapsed time on
stderr. Each answer ends with the token counts and a summary such as
`Summary: llm_calls=6, tool_calls=9, denied=1, tool_errors=0, model_time=24.2s, tool_time=3.1s`.
A denied call still costs an LLM round, because the denial is returned to the
model as the result of that call.

**Scope:** this is a teaching policy, not a sandbox. Allowed tools and
project hooks run with your local permissions. Project hooks are commands
taken from the repository you point the harness at, so only use repositories
you trust. Do not use this lab with untrusted input, production Azure
resources or sensitive repositories. Lab 6 adds human approval as a separate
policy decision.

Labs 3 onward keep this snapshot's tools, built-in policy, project hooks,
rules, progress indicator and run summary for `harness ask`.
