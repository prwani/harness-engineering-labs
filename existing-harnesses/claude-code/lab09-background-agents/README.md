# Lab 9 — Subagents and background agents

**Start from:** `app/` at tag `lab08-done`, with the Lab 0 setup loaded
(see [Working in `app/`](../README.md#working-in-app)).

**Goal:** delegate. A **subagent** runs in its own context window with its
own prompt and tool set, and returns only a summary. A **background
agent** is a whole Claude Code session running detached while you do
something else.

Read the two agent definitions in
[`assets/.claude/agents/`](assets/.claude/agents/):

| Agent | Tools | Job |
|---|---|---|
| `security-reviewer` | Read, Grep, Glob (read-only) | Find input-validation, secret-handling and injection risks |
| `test-writer` | Read, Grep, Glob, Write, Edit, Bash | Add missing tests; mark real app bugs `xfail` instead of "fixing" them |

## 1. Install and inspect

```powershell
Copy-Item -Recurse -Force ..\lab09-background-agents\assets\* .
git add .claude ; git commit -m "chore: add review and test subagents"
```

```sh
cp -R ../lab09-background-agents/assets/. .
git add .claude && git commit -m "chore: add review and test subagents"
```

Start `claude` and run `/agents` to see them (and the built-in ones).

## 2. Run two subagents in parallel

```text
In parallel: use the security-reviewer subagent to review cli.py and pricing.py, and the test-writer subagent to add tests for any untested CLI command. Then give me one combined summary.
```

**Observe:** two `Task`/agent calls start; each has its own transcript
(`Ctrl+O`). The main conversation receives only their summaries, so
`/context` grows far less than if the main agent had read everything
itself. Your Lab 2B hooks still fire on the test-writer's edits. Did the
reviewer stay read-only?

## 3. A background agent

Exit the session and **commit** your work first: a background agent runs
in its own git worktree, created from your last commit, so it won't see
uncommitted changes. Then start it:

```powershell
claude --bg -n coverage "Measure which functions in this project have no direct test and write COVERAGE.md with a table of function, file and tested yes/no. Do not modify code or commit."
claude agents
```

`--bg` prints the agent id. `claude agents` opens an interactive list
(`claude agents --json` for scripts). Keep working in your terminal; check
on it with:

```powershell
claude logs <id>
claude attach <id>     # optional: take it over interactively
```

**Observe:** `git worktree list` shows a second checkout under
`.claude/worktrees/<name>` on a `worktree-<name>` branch. The agent
writes `COVERAGE.md` **there**, not in your `app/` folder. That isolation
is what makes background agents safe to run alongside your own edits.

When it's done, bring the result over and clean up:

```powershell
Copy-Item .claude\worktrees\*\COVERAGE.md .
Remove-Item .claude\worktrees\*\COVERAGE.md
claude rm <id>        # removes the session, its worktree and branch
```

```sh
cp .claude/worktrees/*/COVERAGE.md .
rm .claude/worktrees/*/COVERAGE.md
claude rm <id>
```

`claude rm` refuses to delete a worktree with uncommitted changes, so you
don't lose work by accident.

> Background and parallel agents multiply token cost. Watch `/cost`
> and keep tasks small.

## Record

- Which tools each subagent actually used.
- Main-context size after delegation vs Lab 7's `/context` numbers.
- Whether the background agent finished, and how you'd know if it hadn't.

## Checkpoint

Commit the useful results (new tests, `COVERAGE.md`):

```powershell
python -m pytest -q
git tag lab09-done
```
