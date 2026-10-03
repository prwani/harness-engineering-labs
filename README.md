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

## Build-your-own Harness labs

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

## Use-an-existing-harness labs

Same capability sequence as the build-your-own labs, run against a vendor
CLI instead. Each CLI folder is a fully independent track with its own
setup, config examples and reset scripts — don't mix folders.

| # | [Codex CLI](existing-harnesses/codex-cli) | [Claude Code](existing-harnesses/claude-code) | [GitHub Copilot CLI](existing-harnesses/copilot-cli) |
|---|---|---|---|
| 0 | [Setup](existing-harnesses/codex-cli/lab00-setup) | [Setup](existing-harnesses/claude-code/lab00-setup) | [Setup](existing-harnesses/copilot-cli/lab00-setup) |
| 1 | [Constrained baseline](existing-harnesses/codex-cli/lab01-baseline) | [Constrained baseline](existing-harnesses/claude-code/lab01-baseline) | [Constrained baseline](existing-harnesses/copilot-cli/lab01-baseline) |
| 2A | [Tool loop](existing-harnesses/codex-cli/lab02-tool-loop) | [Tool loop](existing-harnesses/claude-code/lab02-tool-loop) | [Tool loop](existing-harnesses/copilot-cli/lab02-tool-loop) |
| 2B | [Hooks and policy](existing-harnesses/codex-cli/lab02b-hooks) | [Hooks and policy](existing-harnesses/claude-code/lab02b-hooks) | [Hooks and policy](existing-harnesses/copilot-cli/lab02b-hooks) |
| 3 | [Sessions](existing-harnesses/codex-cli/lab03-sessions) | [Sessions](existing-harnesses/claude-code/lab03-sessions) | [Sessions](existing-harnesses/copilot-cli/lab03-sessions) |
| 4 | [Planning](existing-harnesses/codex-cli/lab04-planning) | [Planning](existing-harnesses/claude-code/lab04-planning) | [Planning](existing-harnesses/copilot-cli/lab04-planning) |
| 5 | [File memory](existing-harnesses/codex-cli/lab05-file-memory) | [File memory](existing-harnesses/claude-code/lab05-file-memory) | [File memory](existing-harnesses/copilot-cli/lab05-file-memory) |
| 6 | [Approval](existing-harnesses/codex-cli/lab06-approval) | [Approval](existing-harnesses/claude-code/lab06-approval) | [Approval](existing-harnesses/copilot-cli/lab06-approval) |
| 7 | [Observability](existing-harnesses/codex-cli/lab07-observability) | [Observability](existing-harnesses/claude-code/lab07-observability) | [Observability](existing-harnesses/copilot-cli/lab07-observability) |
| 8 | [Skills and MCP](existing-harnesses/codex-cli/lab08-skills-tools) | [Skills and MCP](existing-harnesses/claude-code/lab08-skills-tools) | [Skills and MCP](existing-harnesses/copilot-cli/lab08-skills-tools) |
| 9 | [Delegation](existing-harnesses/codex-cli/lab09-background-agents) | [Delegation](existing-harnesses/claude-code/lab09-background-agents) | [Delegation](existing-harnesses/copilot-cli/lab09-background-agents) |
| 10 | [Compaction](existing-harnesses/codex-cli/lab10-compaction) | [Compaction](existing-harnesses/claude-code/lab10-compaction) | [Compaction](existing-harnesses/copilot-cli/lab10-compaction) |
| 11 | [Loops](existing-harnesses/codex-cli/lab11-loops) | [Loops](existing-harnesses/claude-code/lab11-loops) | [Loops](existing-harnesses/copilot-cli/lab11-loops) |
| 12 | [Graphs](existing-harnesses/codex-cli/lab12-graphs) | [Graphs](existing-harnesses/claude-code/lab12-graphs) | [Graphs](existing-harnesses/copilot-cli/lab12-graphs) |
| 13 | [Capstone](existing-harnesses/codex-cli/lab13-capstone) | [Capstone](existing-harnesses/claude-code/lab13-capstone) | [Capstone](existing-harnesses/copilot-cli/lab13-capstone) |
| 14 | [Comparison](existing-harnesses/codex-cli/lab14-comparison) | [Comparison](existing-harnesses/claude-code/lab14-comparison) | [Comparison](existing-harnesses/copilot-cli/lab14-comparison) |

These are not scored runs comparable to the build-your-own path: vendor
CLIs own their loop and may expose built-in tools even in read-only mode.
See each track's own README for its Foundry auth model (key vs. Entra ID)
and reset/cleanup steps. The [Codex SDK path](existing-harnesses/codex-sdk)
is reserved for later.

## Repository map

- [`lab-outline.md`](lab-outline.md) — the full course outline: mental model,
  design principles, anchor scenario, and per-lab details.
- [`AGENTS.md`](AGENTS.md) — repository map and conventions for agents
  working in this repo.
- `labs/` — one runnable snapshot per lab.
- [`existing-harnesses/`](existing-harnesses/) — use an existing harness;
  separate Codex CLI, Claude Code and Copilot CLI exercises, and a
  reserved Codex SDK path.
