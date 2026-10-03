# Lab 3 contract

- `lab.json` declares this snapshot's capabilities and resource-dependent live checks.
- `harness lab-info` renders the declaration without requiring cloud access.
- `pytest checks/` runs offline without Foundry, ACA, MCP servers, or telemetry resources.
- This folder is standalone and retains all checks from preceding labs.

## Capability additions

- JSONL session persistence: `run_tool_loop(..., history=, on_message=)` appends
  each question, turn and tool result; `Session.save()` writes each one as it happens
- `SessionStore` under `$HARNESS_HOME/projects/<project>/sessions/` (default
  `~/.harness`): create, list, find by ID, prefix or name, continue, resume, fork
- resume recovery: a tool call without a saved result is paired with an explicit
  "interrupted" result
- history validation across many questions in one conversation
- CLI: `harness ask -n NAME | -c | -r REF [--fork]`, `harness sessions`,
  `/session` and `/history` at the interactive prompt

`harness ask` retains the Lab 2B tool loop: file, test, repository and CLI tools
run behind the built-in command policy, project hooks and rules, and each answer
reports elapsed time plus LLM/tool call counts.
