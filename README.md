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
| 3 | [History and sessions](labs/lab03-sessions) | Named, continued, resumed and forked JSONL sessions; `harness sessions` |
| 4 | [Planning and todos](labs/lab04-planning) | Read-only plan mode, `write_todos`, human `/execute` switch |
| 5 | [File memory and access](labs/lab05-file-memory) | User, project and local `HARNESS.md` memory; `/memory`, `/init` |
| 6 | [Tool approval and safety gates](labs/lab06-approval) | Allow, ask and deny permission rules; `--accept-edits`; `harness permissions` |
| 7 | [Observability and prompt caching](labs/lab07-observability) | JSONL trace events, `harness trace` timings, tokens, cache and cost |
| 8 | [Agent skills and tool scaling](labs/lab08-skills-tools) | On-demand `SKILL.md` skills; stdio MCP servers via `harness mcp` |
| 9 | [Subagents and background agents](labs/lab09-background-agents) | `.harness/agents` subagents; `harness ask --bg` in git worktrees |
| 10 | [Context and compaction](labs/lab10-compaction) | `/compact`, `/clear`, `--compact-at`, ranged `read_file` |
| 11 | [Loops with a stop condition](labs/lab11-loops) | `stop` hooks with bounded retries, `--max-iterations` |
| 12 | [Graphs: routing between specialised agents](labs/lab12-graphs) | `harness route`: classifier and tool-restricted specialists |
| 13 | [Capstone: planner, generator, evaluator](labs/lab13-capstone) | `harness pge`: plan, human gate, generate, fresh evaluator, revisions |
| 14 | [Cross-harness comparison](labs/lab14-native-harness) | Same task in two harnesses; `harness trace`, `harness features` |

## Repository map

- [`lab-outline.md`](lab-outline.md) — the full course outline: mental model,
  design principles, anchor scenario, and per-lab details.
- [`AGENTS.md`](AGENTS.md) — repository map and conventions for agents
  working in this repo.
- `labs/` — one runnable snapshot per lab.
- [`existing-harnesses/`](existing-harnesses/) — use an existing harness;
  separate Codex CLI, Claude Code and Copilot CLI exercises, and a
  reserved Codex SDK path.
