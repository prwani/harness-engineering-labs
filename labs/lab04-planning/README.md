---
layout: default
title: "Lab 4 — Planning and todos"
---

# Lab 4 — Planning and todos

So far the agent decides each next step as it goes, and it can edit files
from the first question. This standalone snapshot separates **deciding
what to do** from **doing it**. `harness ask` gets a **plan mode** in which
the model can investigate but has no way to edit, and a harness-owned
**todo list** that carries the plan into execution.

You plan a multi-file feature, change the plan before any edit, approve
it, then compare what was planned with what was done. The exercise matches
the [Claude Code Lab 4](../../existing-harnesses/claude-code/lab04-planning/).

## What changes

- [`harness/plan_mode.py`](harness/plan_mode.py):
  - In plan mode the write tools are **not offered** to the model, and a
    `pre_tool` policy denies anything that could change the repository:
    write tools and Git subcommands other than read-only ones (`status`,
    `diff`, `log`, `show`, listing `branch`/`tag`, ...). Hiding the tools
    and denying the calls are two layers; the denial catches a model that
    calls a tool it wasn't offered.
  - `write_todos` is the only way the model changes the todo list. It
    sends the whole list each time and marks finished items done.
  - Every question's system prompt includes the mode instructions and the
    open todos, so the plan stays in view as the conversation grows.
- [`harness/learner.py`](harness/learner.py): `ask_with_tools(...,
  mode="plan"|"execute", todos=..., on_todos=...)`.
- [`harness/chat.py`](harness/chat.py): `Chat` holds the mode and the todo
  list. The list is saved next to the session as `<id>.todos.json`, so
  `-c` and `-r` restore it.
- Only the **human** switches modes. There is no tool for it, so the model
  cannot grant itself write access. In the CLI:
  - `harness ask --plan` starts in plan mode; the prompt shows `You [plan]>`.
  - `/plan` switches to plan mode.
  - `/execute [extra instructions]` approves the plan, switches to execute
    mode and tells the model to implement it.
  - `/todos` shows the list.

[`harness/planning.py`](harness/planning.py),
[`harness/todos.py`](harness/todos.py) and
[`harness/writes.py`](harness/writes.py) are the earlier in-process models
of agent specs, todos and idempotent writes; `plan_mode.py` reuses
`TodoList`.

## Learner steps

**Start from:** `labs/app/` at tag `lab03-done` (see the
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

2. **Plan without editing.** Branch first, so approving the plan is cheap
   to undo:

   ```bash
   git switch -c feature/discount-codes
   harness ask -n discount-codes --plan
   ```

   ```text
   Add discount codes to orders:
   - codes live in a new discounts.csv: code,kind,value,expires (kind is percent or cents)
   - SAVE10 = 10 percent, FLAT500 = 500 cents off, plus one already-expired code
   - `python cli.py total P1:2 --code SAVE10` applies it; expired or unknown codes are rejected with a clear message
   - a discount can never make the total negative
   Plan this change.
   ```

   **Observe:** the tool lines show only reads, Git reads and
   `write_todos`. The answer is a plan, and `/todos` shows the steps the
   model recorded. If the model tries a write anyway, you see a `Hook: denied`
   line naming plan mode. `git status` in another terminal shows nothing
   changed.

3. **Steer the plan.** Don't approve yet. Still in plan mode:

   ```text
   Changes: use a dataclass for discount codes, no new dependencies, apply the discount before tax, and list every test you will add.
   ```

   **Observe:** the plan and `/todos` are revised. Copy the final plan into
   `PLAN-discount-codes.md` yourself so you can compare it later.

4. **Approve and implement.**

   ```text
   /execute
   ```

   The prompt changes back to `You>` and the model gets the write tools.
   **Observe** the todos being ticked off with `write_todos` as it works,
   and check `/todos` at the end. Unlike Claude Code, this harness doesn't
   ask before each edit yet; that's Lab 6. When the tests pass, ask it to
   commit on the branch, then `/exit`.

   If you `/exit` part-way, `harness ask -c` restores both the
   conversation and the todo list.

5. **Compare plan vs reality.**

   ```bash
   git diff --stat main
   ```

   Same files as the plan? Every promised test present? Anything it did
   that the plan didn't mention? Did your feedback (dataclass, before tax)
   land in the code? When you're satisfied, merge:

   ```bash
   git switch main && git merge --no-ff feature/discount-codes
   ```

6. **Record**
   - Tools used in plan mode vs after `/execute`, and any `Hook: denied` lines.
   - Differences between the final plan and `git diff --stat`.
   - Whether the open todos matched what was actually left to do.

7. **Checkpoint.** In `app/`:

   ```bash
   python -m pytest -q
   git tag lab04-done
   ```

8. Back in the lab folder, run the offline checks and inspect the declared
   capabilities:

   ```bash
   pytest checks/
   harness lab-info
   ```

`harness ask` keeps the sessions from Lab 3 and the Lab 2B tools, built-in
policy, project hooks and rules. This is a teaching harness, not a
sandbox: only use it on the practice app.
