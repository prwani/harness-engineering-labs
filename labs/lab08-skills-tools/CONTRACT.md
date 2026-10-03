# Lab 8 contract

- `lab.json` declares this snapshot's capabilities and resource-dependent live checks.
- `harness lab-info` renders the declaration without requiring cloud access.
- `pytest checks/` runs offline without Foundry, ACA, MCP servers, or telemetry resources.
  The MCP checks start the bundled `orders_mcp.py` as a local subprocess.
- This folder is standalone and retains all checks from preceding labs.

## Capability additions

- skills: `.harness/skills/<name>/SKILL.md` (project) and
  `$HARNESS_HOME/skills/<name>/SKILL.md` (user); name and description in the
  system prompt, body loaded by the `use_skill` tool or `/<skill-name>`
- a skill's `allowed-tools` are pre-approved permission rules once it is in use
- stdio MCP client: `initialize`, `tools/list`, `tools/call`; tools exposed as
  `mcp__<server>__<tool>` behind the same hooks, permissions and trace
- CLI: `harness mcp add NAME -- COMMAND...`, `harness mcp list`,
  `harness mcp remove NAME`, `harness skills`, `/skills`, `/mcp`
- [`orders_mcp.py`](orders_mcp.py) and
  [`assets/.harness/skills/release-notes/SKILL.md`](assets/.harness/skills/release-notes/SKILL.md)
- in-process models of a skill registry, tool discovery and MCP namespacing
  (`skills.py`)

`harness ask` retains Lab 7 tracing, Lab 6 permissions, Lab 5 file memory, Lab 4
plan mode and todos, Lab 3 sessions and the Lab 2B tool loop: file, test,
repository and CLI tools run behind the built-in command policy, project hooks
and rules, and each answer reports elapsed time plus LLM/tool call counts.
