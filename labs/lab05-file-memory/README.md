---
layout: default
title: "Lab 5 — File memory and access"
---

# Lab 5 — File memory and access

Sessions (Lab 3) keep one *conversation*. Conventions your team wants
followed in *every* conversation ("money is integer cents", "use
Conventional Commits") need a durable home that is reviewed and versioned
like code. This standalone snapshot gives `harness ask` **file memory**:
plain Markdown files named `HARNESS.md`, the equivalent of Claude Code's
`CLAUDE.md` or Codex's `AGENTS.md`, that the harness adds to the system
prompt.

You generate a starting file, add conventions, and test whether a fresh
session follows them unprompted and when an edit takes effect. The
exercise matches the
[Claude Code Lab 5](../../existing-harnesses/claude-code/lab05-file-memory/).

## What changes

- [`harness/project_memory.py`](harness/project_memory.py) reads up to
  three files, broadest first, so a later file can refine an earlier one:

  | Scope | File | Shared? |
  |---|---|---|
  | user | `~/.harness/HARNESS.md` (`$HARNESS_HOME`) | only you, every project |
  | project | `HARNESS.md` in the project | the team, via git |
  | local | `HARNESS.local.md` in the project | only you; gitignore it |

  Each file is capped at 20,000 characters (truncation is marked), because
  every line is sent with every model call.
- [`harness/learner.py`](harness/learner.py) adds the memory to the system
  prompt **for every question**, so an edit applies to the next question in
  the same session. (Many harnesses read memory once at session start
  instead; step 4 compares.)
- The CLI:
  - `/memory` at the prompt, or `harness memory files`, lists the three
    locations and which are loaded.
  - `/init [extra instructions]` asks the model to explore the project and
    write a starting `HARNESS.md`.

Memory is guidance for the model, not enforcement. A rule that must always
hold belongs in a hook (Lab 2B), like `protect_catalog.py`.
[`harness/memory.py`](harness/memory.py) keeps the earlier in-process
models of session memory, shared-store concurrency and path scopes.

## Learner steps

**Start from:** `labs/app/` at tag `lab04-done` (see the
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

2. **Generate a starting HARNESS.md.**

   ```bash
   harness ask
   ```

   ```text
   /init
   ```

   **Observe:** the model reads the project and writes `HARNESS.md`
   (install and test commands, modules). `/exit`, then read it. Is anything
   wrong or invented?

3. **Add your team's conventions.** Open `HARNESS.md` in your editor and
   add a short section. Every line costs context in every model call:

   ```markdown
   ## Conventions
   - Money is always integer cents. Never use float for prices or totals.
   - Run `python -m pytest -q` and see it pass before saying a task is done.
   - Commit messages follow Conventional Commits (feat:, fix:, docs:, chore:, test:).
   - Never edit catalog.csv; catalog changes come from the warehouse sync.
   ```

   ```bash
   git add HARNESS.md && git commit -m "docs: add HARNESS.md"
   ```

4. **Fresh session: is the memory followed?** Start a **new** session
   (not `-c`):

   ```bash
   harness ask -n gift-wrap
   ```

   ```text
   Add an optional gift-wrap fee of 299 cents per order, as a --gift-wrap flag on the total command. Commit when done.
   ```

   **Observe, without reminding it:** integer cents? Tests run before
   "done"? A `feat:` commit message? Type `/memory` to see which files are
   loaded.

5. **Edit memory mid-session.** Without leaving, add a line to `HARNESS.md`
   in your editor:

   ```markdown
   - Every public function has a one-line docstring.
   ```

   Then ask in the same session:

   ```text
   Add a function that returns the most expensive product in the catalog.
   ```

   **Observe:** the new rule applies straight away, because this harness
   rereads memory for every question. The trade-off: a system prompt that
   changes between calls can't reuse a provider's prompt cache. In Claude
   Code the same experiment may need a fresh session; compare if you did
   that track.

6. **Personal vs project memory.** For notes only you want, create
   `HARNESS.local.md` and gitignore it, or use `~/.harness/HARNESS.md` for
   every project:

   ```bash
   echo "HARNESS.local.md" >> .gitignore
   echo "- Explain your plan in one sentence before editing." > HARNESS.local.md
   git add .gitignore && git commit -m "chore: ignore personal harness memory"
   harness memory files
   ```

   Don't put secrets in any memory file: they are sent to the model with
   every call.

7. **Record**
   - Which conventions were followed unprompted, and which weren't.
   - Whether a mid-session edit took effect, and the cost of rereading.
   - One thing that belongs in a hook rather than in memory, and why.
     (`protect_catalog.py` already enforces the catalog rule; what does
     the memory line add?)

8. **Checkpoint.** In `app/`:

   ```bash
   python -m pytest -q && git status
   git tag lab05-done
   ```

9. Back in the lab folder, run the offline checks and inspect the declared
   capabilities:

   ```bash
   pytest checks/
   harness lab-info
   ```

`harness ask` keeps plan mode and todos (Lab 4), sessions (Lab 3) and the
Lab 2B tools, built-in policy, project hooks and rules. This is a teaching
harness, not a sandbox: only use it on the practice app.
