# Lab 5 contract

- `lab.json` declares this snapshot's capabilities and resource-dependent live checks.
- `harness lab-info` renders the declaration without requiring cloud access.
- `pytest checks/` runs offline without Foundry, ACA, MCP servers, or telemetry resources.
- This folder is standalone and retains all checks from preceding labs.

## Capability additions

- file memory: user `$HARNESS_HOME/HARNESS.md`, project `HARNESS.md` and local
  `HARNESS.local.md`, loaded broadest first into the system prompt, capped at
  20,000 characters per file
- memory is reread for every question, so edits apply mid-session
- CLI: `/memory`, `/init [instructions]`, `harness memory files`
- in-process models of session memory, optimistic concurrency and path scopes
  (`memory.py`)

`harness ask` retains Lab 4 plan mode and todos, Lab 3 sessions and the Lab 2B
tool loop: file, test, repository and CLI tools run behind the built-in command
policy, project hooks and rules, and each answer reports elapsed time plus
LLM/tool call counts.
