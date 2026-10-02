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
| 3 | [History and sessions](labs/lab03-sessions/README.html) | JSONL session persistence, resume recovery, history validation |
| 4 | [Planning and todos](labs/lab04-planning/README.html) | Planner and executor modes, harness-owned todos, idempotent writes |
| 5 | [File memory and access](labs/lab05-file-memory/README.html) | Session memory, optimistic concurrency, path scope enforcement |
| 6 | [Tool approval and safety gates](labs/lab06-approval/README.html) | Tool policy gate, standing approvals, write audit log |
| 7 | [Observability and prompt caching](labs/lab07-observability/README.html) | OpenTelemetry event model, usage cost attribution, result redaction, cache boundaries |
| 8 | [Agent skills and tool scaling](labs/lab08-skills-tools/README.html) | Skill registry, skill approval state, tool discovery metadata, MCP tool namespace |
| 9 | [Background agents and delegation](labs/lab09-background-agents/README.html) | Sub-agent task model, parallel fan-out plan, isolated child transcripts |
| 10 | [Compaction and repository map](labs/lab10-compaction/README.html) | Context compaction policy, summary handoff artifact, repository map metadata |
| 11 | [Loop engineering](labs/lab11-loops/README.html) | Retry, validation, polling, and refinement loop contracts |
| 12 | [Graph engineering](labs/lab12-graphs/README.html) | Typed graph state, conditional routing, idempotent graph nodes, human route confirmation |
| 13 | [Planner, generator, evaluator capstone](labs/lab13-capstone/README.html) | Dynamic planner-generator-evaluator graph, separate evaluator, ablation metadata |
| 14 | [Native harness comparison](labs/lab14-native-harness/README.html) | Comparison scorecard schema, Claude Code mapping, Copilot CLI mapping |

## Repository map

- [`lab-outline.md`](lab-outline.html) — the full course outline: mental
  model, design principles, anchor scenario, and per-lab details.
- [`labs/`](https://github.com/prwani/harness-engineering-labs/tree/main/labs) —
  one runnable snapshot per lab.
- [View source on GitHub](https://github.com/prwani/harness-engineering-labs)
