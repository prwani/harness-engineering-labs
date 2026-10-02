# Lab 9 contract

- `lab.json` declares this snapshot's capabilities and resource-dependent live checks.
- `harness lab-info` renders the declaration without requiring cloud access.
- `pytest checks/` runs offline without Foundry, ACA, MCP servers, or telemetry resources.
  The background-agent check creates a temporary git repository and runs a
  local Python command in its worktree instead of a model.
- This folder is standalone and retains all checks from preceding labs.

## Capability additions

- agent definitions: `.harness/agents/<name>.md` (project) and
  `$HARNESS_HOME/agents/<name>.md` (user) with `name`, `description`, required
  `tools` and the agent's system prompt
- `run_agent(agent, task)`: a child run with a fresh history, the agent's prompt
  and only its tools (others denied), sharing hooks, permissions, MCP tools and
  trace; tool events shown as `agent:tool`; the parent receives only the final
  answer and call counts
- isolated child transcripts in `<session id>.agents/NN-<agent>.jsonl`
- background agents: `harness ask --bg -n NAME`, run detached in a git worktree
  `.harness/worktrees/NAME` on branch `worktree-NAME`; `harness agents`,
  `harness logs NAME`, `harness rm NAME [--force]` (refuses while running or
  with uncommitted changes)
- CLI: `/agents`
- [`assets/.harness/agents/`](assets/.harness/agents/): `security-reviewer` and
  `test-writer`
- in-process model of a sub-agent task plan (`subagents.py`)

`harness ask` retains Lab 8 skills and MCP, Lab 7 tracing, Lab 6 permissions,
Lab 5 file memory, Lab 4 plan mode and todos, Lab 3 sessions and the Lab 2B tool
loop: file, test, repository and CLI tools run behind the built-in command
policy, project hooks and rules, and each answer reports elapsed time plus
LLM/tool call counts.
