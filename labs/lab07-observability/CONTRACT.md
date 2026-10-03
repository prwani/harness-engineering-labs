# Lab 7 contract

- `lab.json` declares this snapshot's capabilities and resource-dependent live checks.
- `harness lab-info` renders the declaration without requiring cloud access.
- `pytest checks/` runs offline without Foundry, ACA, MCP servers, or telemetry resources.
- This folder is standalone and retains all checks from preceding labs.

## Capability additions

- `harness ask --trace FILE`: JSONL events `run_start`, `model_call`, `tool_call`,
  `tool_result`, `denied`, `hook`, `permission`, `run_end`, with redacted and
  truncated arguments and results
- `MeteredClient` measures every model call without changing it
- `harness trace FILE [--input-price --output-price]` summary, with an estimated
  cost from user-supplied prices (`HARNESS_PRICE_INPUT`/`HARNESS_PRICE_OUTPUT`)
- `/cost` and `/context` at the interactive prompt
- the earlier span model, cost attribution, redaction and cache boundaries
  (`telemetry.py`)

`harness ask` retains Lab 6 permissions, Lab 5 file memory, Lab 4 plan mode and
todos, Lab 3 sessions and the Lab 2B tool loop: file, test, repository and CLI
tools run behind the built-in command policy, project hooks and rules, and each
answer reports elapsed time plus LLM/tool call counts.
