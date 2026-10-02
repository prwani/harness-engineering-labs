# Lab 14 contract

- `lab.json` declares this snapshot's capabilities and resource-dependent live checks.
- `harness lab-info` renders the declaration without requiring cloud access.
- `pytest checks/` runs offline without Foundry, ACA, MCP servers, or telemetry resources.
- This folder is standalone and retains all checks from preceding labs.

## Capability additions

- `harness features`: each capability from Labs 2–13, the command or file that
  drives it, and its Claude Code counterpart
- the comparison uses existing measurement: `harness ask --trace` and
  `harness trace` (Lab 7)
- comparison scorecard schema and layer mappings (`native_harness.py`)

`harness` retains every capability from Labs 2–13: `harness ask` with stop
hooks, compaction, subagents and background agents, skills and MCP, tracing,
permissions, file memory, plan mode and todos, sessions and the Lab 2B tool loop;
`harness route` and `harness pge`.
