# Lab 6 contract

- `lab.json` declares this snapshot's capabilities and resource-dependent live checks.
- `harness lab-info` renders the declaration without requiring cloud access.
- `pytest checks/` runs offline without Foundry, ACA, MCP servers, or telemetry resources.
- This folder is standalone and retains all checks from preceding labs.

## Capability additions

- permission rules `tool` / `tool(glob)` in the `permissions` section of user
  (`$HARNESS_HOME/settings.json`), project (`.harness/settings.json`) and local
  (`.harness/settings.local.json`) settings; deny > ask > allow, then defaults
  (reads allow; edits, non-read-only Git and unknown tools ask)
- interactive approval (yes / no / always for this session) as the last
  `pre_tool` check; with no one to answer, ask means deny
- CLI: `harness ask --accept-edits`, `/permissions`, `harness permissions`
- [`assets/.harness/settings.json`](assets/.harness/settings.json): the lab's
  rules plus the Lab 2B hooks
- in-process models of the policy table, standing approvals and an audit log
  (`approval.py`)

`harness ask` retains Lab 5 file memory, Lab 4 plan mode and todos, Lab 3 sessions
and the Lab 2B tool loop: file, test, repository and CLI tools run behind the
built-in command policy, project hooks and rules, and each answer reports elapsed
time plus LLM/tool call counts.
