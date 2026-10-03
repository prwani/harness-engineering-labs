# Lab 10 contract

- `lab.json` declares this snapshot's capabilities and resource-dependent live checks.
- `harness lab-info` renders the declaration without requiring cloud access.
- `pytest checks/` runs offline without Foundry, ACA, MCP servers, or telemetry resources.
- This folder is standalone and retains all checks from preceding labs.

## Capability additions

- `/compact [instructions]`: a model-written summary, steered by optional
  instructions, replaces the session history; tool definitions are still sent
  with the summary request
- session files keep the full record; a `reset` entry marks where a resumed
  session starts
- `/clear` empties the history
- `harness ask --compact-at TOKENS`: compact before a question once the last
  request reached that many input tokens
- `/context` reports the current history size; traces record `compact` events
- `read_file` reads line ranges (`start_line`, `max_lines` up to 1000) of files
  up to 10 MB and reports truncation
- [`make_log.py`](make_log.py): a deterministic 6,000-line incident log
- in-process models of a compaction policy, summary handoff and repository map
  (`compaction.py`)

`harness ask` retains Lab 9 subagents and background agents, Lab 8 skills and
MCP, Lab 7 tracing, Lab 6 permissions, Lab 5 file memory, Lab 4 plan mode and
todos, Lab 3 sessions and the Lab 2B tool loop: file, test, repository and CLI
tools run behind the built-in command policy, project hooks and rules, and each
answer reports elapsed time plus LLM/tool call counts.
