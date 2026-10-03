# Lab 12 contract

- `lab.json` declares this snapshot's capabilities and resource-dependent live checks.
- `harness lab-info` renders the declaration without requiring cloud access.
- `pytest checks/` runs offline without Foundry, ACA, MCP servers, or telemetry resources.
- This folder is standalone and retains all checks from preceding labs.

## Capability additions

- `harness route "ticket" [--repo] [--runs]`: a classify -> bug | question |
  feature | escalate graph built on `graph.py`
- the classifier has no tools and must return JSON; unknown or unparseable
  routes escalate
- specialists run as agents with fixed prompts and tool lists (read-only, plus
  `run_tests` for bugs), behind project hooks and permissions; calls that would
  ask are denied
- escalation makes no model call
- one trace per ticket in `.runs/route-<time>.jsonl`, readable with `harness trace`
- typed graph state, conditional routing, idempotent nodes and human route
  confirmation (`graph.py`)

`harness ask` retains Lab 11 stop hooks, Lab 10 compaction, Lab 9 subagents and
background agents, Lab 8 skills and MCP, Lab 7 tracing, Lab 6 permissions, Lab 5
file memory, Lab 4 plan mode and todos, Lab 3 sessions and the Lab 2B tool loop:
file, test, repository and CLI tools run behind the built-in command policy,
project hooks and rules, and each answer reports elapsed time plus LLM/tool call
counts.
