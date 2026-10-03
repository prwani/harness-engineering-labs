# Lab 4 contract

- `lab.json` declares this snapshot's capabilities and resource-dependent live checks.
- `harness lab-info` renders the declaration without requiring cloud access.
- `pytest checks/` runs offline without Foundry, ACA, MCP servers, or telemetry resources.
- This folder is standalone and retains all checks from preceding labs.

## Capability additions

- plan mode: write tools are not offered, and a `pre_tool` policy denies write
  tools and non-read-only Git subcommands
- harness-owned todos: the `write_todos` tool, an open-todo reminder in every
  question's system prompt, saved next to the session as `<id>.todos.json`
- human-only mode switch: `harness ask --plan`, `/plan`, `/execute [instructions]`,
  `/todos`
- in-process models of planner/executor specs, todos and idempotent writes
  (`planning.py`, `todos.py`, `writes.py`)

`harness ask` retains the Lab 3 sessions and the Lab 2B tool loop: file, test,
repository and CLI tools run behind the built-in command policy, project hooks
and rules, and each answer reports elapsed time plus LLM/tool call counts.
