---
layout: default
title: "Build-your-own harness labs"
---

# Build-your-own harness labs

Each `labNN-*` folder is a standalone snapshot of a small Python harness,
called `harness`. The snapshots build on each other, one capability per lab.
The goal is a harness that is **small enough to read in full** and still does
real work, so you can see what each capability adds. It is not meant to be a
production replacement for Claude Code or Codex.

The [Claude Code track](../existing-harnesses/claude-code/) covers the same
capabilities using an existing harness. Both tracks use **the same practice
app**: a synthetic pet-store order calculator that you build in Lab 2A and
keep extending. That makes it straightforward to compare the two harnesses on
the same work.

## Working in `labs/app/`

```text
labs/
├── app/            # Lab 0, gitignored: YOUR practice app (its own git repo)
├── lab00-setup/    # each lab: its own .venv, .env, harness code and checks
├── lab02b-hooks/
│   └── assets/     # files you copy into app/ (hooks, rules, ...)
└── ...
```

Each lab is installed on its own, from its own folder, into its own `.venv`
with its own `.env`. You **use** each lab's harness from `app/`:

```bash
cd labs/lab02-tool-loop
python -m venv .venv
. .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
pip install -e '.[dev]'
cp .env.example .env           # non-secret Foundry settings only (Entra-only)
az login
cd ../app
harness ask
```

The `harness` command finds the `.env` file in the lab folder where it was
installed, even when you run it from `app/`. The tools run in the current
directory (or `--repo PATH`), so the agent only works on the practice app.

**Checkpoints are git tags in `app/`.** Each lab ends with
`git tag labNN-done`, and each lab README says which tag it starts from. The
model's output varies between runs, so your code will differ from other
learners' code. That is expected: the prompts describe goals, not exact
code. To redo a lab, return to its starting tag:

```bash
cd labs/app
git switch main
git reset --hard lab02a-done   # the tag the lab starts from
git clean -fd
```

## Labs and the practice app

| Lab | Harness capability | What you do to the app |
|---|---|---|
| [0](lab00-setup/) | Foundry setup, two provider APIs | Create `app/` as a git repo; make a live call |
| [1](lab01-bare-call/) | Bare model call | Ask about the app: a bare model can't see it |
| [2A](lab02-tool-loop/) | Tool loop with file, test, Git and shell tools | Build the app; find a regression with git history |
| [2B](lab02b-hooks/) | Hooks and scoped rules | Pricing rule; hooks that block catalog edits and run tests |
| [3](lab03-sessions/)–[14](lab14-native-harness/) | Sessions, planning, memory, approval, observability, skills, subagents, compaction, loops, graphs, capstone, comparison | Practice-app exercises are being added in later phases. Until then, follow each lab's existing steps. `harness ask` in these labs already uses the Lab 2B tools and hooks. |

## Safety

The tools run with your operating-system permissions. Lab 2A is
intentionally unrestricted. From Lab 2B on, hooks deny `shell` and
destructive Git commands, but that is a teaching policy, not a sandbox.
Project hooks in `.harness/settings.json` are commands the harness runs for
you, so only use a project you trust. Use the synthetic data these labs
create. Never put keys or tokens in `.env`, prompts or the app.
