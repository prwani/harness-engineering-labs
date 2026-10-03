# Lab 13 contract

- `lab.json` declares this snapshot's capabilities and resource-dependent live checks.
- `harness lab-info` renders the declaration without requiring cloud access.
- `pytest checks/` runs offline without Foundry, ACA, MCP servers, or telemetry resources.
- This folder is standalone and retains all checks from preceding labs.

## Capability additions

- `harness pge "feature" [--max-revisions N] [--no-evaluator] [--repo] [--runs]`
- planner (read-only) writes `PLAN.md`; a human gate confirms before any edit
- generator with edit and test tools, edits accepted, no prompts
- evaluator in a fresh context with read, test and read-only git tools; JSON
  verdict, anything unparseable is FAIL
- bounded revision loop feeding the evaluator's failed criteria back to the
  generator
- one trace per run in `.runs/pge-<time>.jsonl` with `node` and `verdict` events
- `--no-evaluator` ablation
- in-process model of the planner-generator-evaluator graph with ablation
  metadata (`capstone.py`)

`harness ask` retains Lab 11 stop hooks, Lab 10 compaction, Lab 9 subagents and
background agents, Lab 8 skills and MCP, Lab 7 tracing, Lab 6 permissions, Lab 5
file memory, Lab 4 plan mode and todos, Lab 3 sessions and the Lab 2B tool loop;
`harness route` (Lab 12) is retained.
