# Lab 11 contract

- `lab.json` declares this snapshot's capabilities and resource-dependent live checks.
- `harness lab-info` renders the declaration without requiring cloud access.
- `pytest checks/` runs offline without Foundry, ACA, MCP servers, or telemetry resources.
  The asset checks run the bundled stop gate (pytest) in a temporary folder.
- This folder is standalone and retains all checks from preceding labs.

## Capability additions

- `stop` hooks in `.harness/settings.json`: run on the final answer with the
  event on stdin; exit code 2 sends stderr back and the loop continues
- the tool loop bounds stop hooks to 3 blocks per question and reports
  `stop_blocks` in the summary and trace
- `harness ask --max-iterations N`: model calls per question, including
  stop-hook retries
- stop hooks are skipped in plan mode and for subagents
- [`assets/`](assets/): the bulk-discount spec, `stop_gate.py`, and settings that
  deny edits to the spec
- in-process models of retry, validation, polling and refinement loops
  (`loops.py`)

`harness ask` retains Lab 10 compaction, Lab 9 subagents and background agents,
Lab 8 skills and MCP, Lab 7 tracing, Lab 6 permissions, Lab 5 file memory, Lab 4
plan mode and todos, Lab 3 sessions and the Lab 2B tool loop: file, test,
repository and CLI tools run behind the built-in command policy, project hooks
and rules, and each answer reports elapsed time plus LLM/tool call counts.
