---
layout: default
title: "Lab 9 — Subagents and background agents"
---

# Lab 9 — Subagents and background agents

This standalone snapshot teaches `harness ask` to delegate in two ways:

- a **subagent** runs in its own context window, with its own prompt and
  tool set, and returns only a summary to the main conversation.
- a **background agent** is a whole `harness ask` run, detached, in its
  own git worktree, while you keep working.

The exercise matches the
[Claude Code Lab 9](../../existing-harnesses/claude-code/lab09-background-agents/).

## What changes

- [`harness/agents.py`](harness/agents.py):
  - Agents live in `.harness/agents/<name>.md` in the project, or
    `~/.harness/agents/<name>.md` for you alone. Front matter gives the
    `name`, a `description` and a required `tools` list (exact names or
    patterns such as `mcp__orders__*`); the body is the agent's system
    prompt.
  - The main conversation sees each agent's name and description and a
    `run_agent(agent, task)` tool. Delegating is allowed by default; the
    agent's own tool calls are checked as usual.
- [`harness/chat.py`](harness/chat.py) runs each `run_agent` call as a
  child:
  - a fresh history containing only the task, the agent's prompt, and only
    the tools it lists. A built-in policy denies any other tool.
  - the same hooks, permissions, MCP tools, model client and trace as the
    parent. Its tool lines are shown as `agent:tool`.
  - its own transcript, next to the session file:
    `~/.harness/projects/<project>/sessions/<id>.agents/NN-<agent>.jsonl`.
  - The parent receives one tool result: the agent's final answer, with
    its call counts and transcript path.
  - Agents can't start other agents, and they run one after another; this
    harness has no parallel fan-out.
- [`harness/background.py`](harness/background.py):
  - `harness ask --bg -n NAME "task"` creates a git worktree at
    `.harness/worktrees/NAME` on branch `worktree-NAME`, from your last
    commit, and starts a detached `harness ask` there with
    `--accept-edits` (there's nobody to answer a prompt) and `--trace`.
  - `harness agents` lists background agents and their status;
    `harness logs NAME` shows the output so far.
  - `harness rm NAME` removes the worktree, the branch and the records. It
    refuses while the agent is running or if the worktree has uncommitted
    changes (`--force` discards them).
- `/agents` lists the available agent definitions.

[`harness/subagents.py`](harness/subagents.py) keeps the earlier
in-process model of a sub-agent task plan with isolated child transcripts.

## Learner steps

**Start from:** `labs/app/` at tag `lab08-done` (see the
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

### Part A: subagents

2. Read the two agent definitions in
   [`assets/.harness/agents/`](assets/.harness/agents/):

   | Agent | Tools | Job |
   |---|---|---|
   | `security-reviewer` | `list_files`, `read_file`, `git_status`, `git_log` (read-only) | Find input-validation, secret-handling and money bugs |
   | `test-writer` | `list_files`, `read_file`, `write_file`, `edit_file`, `run_tests` | Add missing tests; mark real app bugs `xfail` instead of "fixing" them |

   Install and commit them:

   ```bash
   cp -R ../lab09-background-agents/assets/. .
   git add .harness && git commit -m "chore: add review and test subagents"
   ```

3. Delegate:

   ```bash
   harness ask -n delegate
   ```

   Type `/agents`, then:

   ```text
   Use the security-reviewer agent to review cli.py and pricing.py, and the test-writer agent to add tests for any untested CLI command. Then give me one combined summary.
   ```

   **Observe:**
   - two `run_agent` calls, each followed by lines such as
     `Tool: security-reviewer:read_file(...)`.
   - your Lab 6 permission prompts (and Lab 2B hooks) still apply to the
     test-writer's edits.
   - did the reviewer stay read-only? Any tool outside its list is shown as
     `Hook: denied security-reviewer:...`.
   - `/context`: the main conversation holds the two summaries, not the
     files the agents read. Compare with Lab 7's numbers. Each agent's full
     transcript is in the `.agents/` folder named in its result.

   `/exit` when done, review the new tests, and commit what you keep.

### Part B: a background agent

4. Commit your work first: the background agent's worktree is created
   from your last commit, so it won't see uncommitted changes. Keep the
   worktrees out of git:

   ```bash
   echo ".harness/worktrees/" >> .gitignore
   git add .gitignore && git commit -m "chore: ignore agent worktrees"
   ```

5. Start it:

   ```bash
   harness ask --bg -n coverage "Measure which functions in this project have no direct test and write COVERAGE.md with a table of function, file and tested yes/no. Do not modify code or commit."
   harness agents
   ```

   Keep working in your terminal; check on it with:

   ```bash
   harness logs coverage
   ```

   **Observe:** `git worktree list` shows a second checkout under
   `.harness/worktrees/coverage` on a `worktree-coverage` branch. The agent
   writes `COVERAGE.md` **there**, not in your `app/` folder. That
   isolation is what makes it safe to run alongside your own edits.

6. When `harness agents` shows `done`, bring the result over and clean up:

   ```bash
   cp .harness/worktrees/coverage/COVERAGE.md .
   rm .harness/worktrees/coverage/COVERAGE.md
   harness rm coverage
   ```

   ```powershell
   Copy-Item .harness\worktrees\coverage\COVERAGE.md .
   Remove-Item .harness\worktrees\coverage\COVERAGE.md
   harness rm coverage
   ```

   Try `harness rm coverage` **before** removing `COVERAGE.md` from the
   worktree: it refuses, so you don't lose work by accident.

   > Subagents and background agents multiply token cost. Check `/cost`,
   > or `harness trace` on the background agent's trace file (shown by
   > `harness logs`), and keep tasks small.

7. **Record**
   - Which tools each subagent actually used, and any that were denied.
   - Main-context size after delegation vs Lab 7's `/context` numbers.
   - Whether the background agent finished, and how you'd know if it
     hadn't.

8. **Checkpoint.** Commit the useful results (new tests, `COVERAGE.md`),
   then in `app/`:

   ```bash
   python -m pytest -q
   git tag lab09-done
   ```

9. Back in the lab folder, run the offline checks and inspect the declared
   capabilities:

   ```bash
   pytest checks/
   harness lab-info
   ```

`harness ask` keeps skills and MCP (Lab 8), tracing (Lab 7), permissions
(Lab 6), file memory (Lab 5), plan mode and todos (Lab 4), sessions (Lab 3)
and the Lab 2B tools, built-in policy, project hooks and rules. This is a
teaching harness, not a sandbox: only use it on the practice app.
