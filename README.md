# Harness Engineering Labs

This repository offers two paths through harness engineering:

- **Build your own harness:** self-contained Python snapshots in [`labs/`](labs/),
  from a bare model call through tools, planning, memory and orchestration.
- **Use an existing harness:** standalone [Codex CLI](existing-harnesses/codex-cli/),
  [Claude Code](existing-harnesses/claude-code/) and
  [GitHub Copilot CLI](existing-harnesses/copilot-cli/) exercises covering
  the same sequence with vendor-provided behavior and explicit limits on
  what can be disabled or measured. The separate
  [Codex SDK path](existing-harnesses/codex-sdk/) is reserved for later.

Both paths use the same pet-store practice app, so you can compare your
harness with an existing one on the same work. See the
[build-your-own track guide](labs/README.md) for how the labs use `labs/app/`.

Each build-your-own snapshot can be copied or downloaded independently.
Run its checks from inside its directory with `pytest checks/`. Snapshots
do not import from one another. Existing-harness CLI exercises are also
independent; live Foundry use needs learner-provisioned resources and
credentials, and no cross-path scored evaluation is provided.

📖 Browse the published site: **https://prwani.github.io/harness-engineering-labs/**

## Build-your-own labs

| # | Lab | Focus |
|---|-----|-------|
| 0 | [Setup, dual API, and scorecard](labs/lab00-setup) | Entra configuration, dual model adapters, usage ledger, store simulator |
| 1 | [Bare model call](labs/lab01-bare-call) | Stateless bare call, `StoreHealthReport` envelope, deterministic scorecard grading |
| 2A | [Tool loop and unrestricted CLI tools](labs/lab02-tool-loop) | Tool loop with file, test, Git, Azure CLI, and shell tools; build the practice app |
| 2B | [Tool hooks and command policy](labs/lab02b-hooks) | Built-in policy, project hooks, scoped rules, paired denials |
| 3 | [History and sessions](labs/lab03-sessions) | JSONL session persistence, resume recovery, history validation |
| 4 | [Planning and todos](labs/lab04-planning) | Planner and executor modes, harness-owned todos, idempotent writes |
| 5 | [File memory and access](labs/lab05-file-memory) | Session memory, optimistic concurrency, path scope enforcement |
| 6 | [Tool approval and safety gates](labs/lab06-approval) | Tool policy gate, standing approvals, write audit log |
| 7 | [Observability and prompt caching](labs/lab07-observability) | OpenTelemetry event model, usage cost attribution, result redaction, cache boundaries |
| 8 | [Agent skills and tool scaling](labs/lab08-skills-tools) | Skill registry, skill approval state, tool discovery metadata, MCP tool namespace |
| 9 | [Background agents and delegation](labs/lab09-background-agents) | Sub-agent task model, parallel fan-out plan, isolated child transcripts |
| 10 | [Compaction and repository map](labs/lab10-compaction) | Context compaction policy, summary handoff artifact, repository map metadata |
| 11 | [Loop engineering](labs/lab11-loops) | Retry, validation, polling, and refinement loop contracts |
| 12 | [Graph engineering](labs/lab12-graphs) | Typed graph state, conditional routing, idempotent graph nodes, human route confirmation |
| 13 | [Planner, generator, evaluator capstone](labs/lab13-capstone) | Dynamic planner-generator-evaluator graph, separate evaluator, ablation metadata |
| 14 | [Native harness comparison](labs/lab14-native-harness) | Comparison scorecard schema, Claude Code mapping, Copilot CLI mapping |

## Repository map

- [`lab-outline.md`](lab-outline.md) — the full course outline: mental model,
  design principles, anchor scenario, and per-lab details.
- [`AGENTS.md`](AGENTS.md) — repository map and conventions for agents
  working in this repo.
- `labs/` — one runnable snapshot per lab.
- [`existing-harnesses/`](existing-harnesses/) — use an existing harness;
  separate Codex CLI, Claude Code and Copilot CLI exercises, and a
  reserved Codex SDK path.
