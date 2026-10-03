---
layout: default
title: Home
---

# Harness, Loop & Graph Engineering Labs

This site publishes the self-contained Python lab snapshots from
[`prwani/harness-engineering-labs`](https://github.com/prwani/harness-engineering-labs)
for building an agent harness from a bare model call through tool loops,
planning, memory, observability, background agents, loop engineering, and
graph orchestration.

Each lab is a **standalone snapshot** — copy or download any one independently
and run its checks from inside its directory with `pytest checks/`. Snapshots
do not import from one another.

Start with the **[track guide](labs/README.html)** and
**[Lab 0 — Setup](labs/lab00-setup/README.html)**, then work through the labs
in order. From Lab 2A on, you use your harness to build and extend a small
pet-store practice app, the same app as in the Claude Code track. See the full **[Lab Outline](lab-outline.html)**
for the mental model, design principles, and detailed rationale behind the
course.

## Labs

| # | Lab | Focus |
|---|-----|-------|
| 0 | [Setup, dual API, and scorecard](labs/lab00-setup/README.html) | Entra configuration, dual model adapters, usage ledger, store simulator |
| 1 | [Bare model call](labs/lab01-bare-call/README.html) | Stateless bare call, `StoreHealthReport` envelope, deterministic scorecard grading |
| 2A | [Tool loop and unrestricted CLI tools](labs/lab02-tool-loop/README.html) | Tool loop with file, test, Git, Azure CLI, and shell tools; build the practice app |
| 2B | [Tool hooks and command policy](labs/lab02b-hooks/README.html) | Built-in policy, project hooks, scoped rules, paired denials |
| 3 | [History and sessions](labs/lab03-sessions/README.html) | Named, continued, resumed and forked JSONL sessions; `harness sessions` |
| 4 | [Planning and todos](labs/lab04-planning/README.html) | Read-only plan mode, `write_todos`, human `/execute` switch |
| 5 | [File memory and access](labs/lab05-file-memory/README.html) | User, project and local `HARNESS.md` memory; `/memory`, `/init` |
| 6 | [Tool approval and safety gates](labs/lab06-approval/README.html) | Allow, ask and deny permission rules; `--accept-edits`; `harness permissions` |
| 7 | [Observability and prompt caching](labs/lab07-observability/README.html) | JSONL trace events, `harness trace` timings, tokens, cache and cost |
| 8 | [Agent skills and tool scaling](labs/lab08-skills-tools/README.html) | On-demand `SKILL.md` skills; stdio MCP servers via `harness mcp` |
| 9 | [Subagents and background agents](labs/lab09-background-agents/README.html) | `.harness/agents` subagents; `harness ask --bg` in git worktrees |
| 10 | [Context and compaction](labs/lab10-compaction/README.html) | `/compact`, `/clear`, `--compact-at`, ranged `read_file` |
| 11 | [Loops with a stop condition](labs/lab11-loops/README.html) | `stop` hooks with bounded retries, `--max-iterations` |
| 12 | [Graphs: routing between specialised agents](labs/lab12-graphs/README.html) | `harness route`: classifier and tool-restricted specialists |
| 13 | [Capstone: planner, generator, evaluator](labs/lab13-capstone/README.html) | `harness pge`: plan, human gate, generate, fresh evaluator, revisions |
| 14 | [Cross-harness comparison](labs/lab14-native-harness/README.html) | Same task in two harnesses; `harness trace`, `harness features` |

## Repository map

- [`lab-outline.md`](lab-outline.html) — the full course outline: mental
  model, design principles, anchor scenario, and per-lab details.
- [`labs/`](https://github.com/prwani/harness-engineering-labs/tree/main/labs) —
  one runnable snapshot per lab.
- [View source on GitHub](https://github.com/prwani/harness-engineering-labs)
