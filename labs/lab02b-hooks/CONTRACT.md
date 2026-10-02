# Lab 2B contract

- `lab.json` declares this snapshot's capabilities and resource-dependent live checks.
- `harness lab-info` renders the declaration without requiring cloud access.
- `pytest checks/` runs offline without Foundry, ACA, MCP servers, or telemetry resources.
- This folder is standalone and retains all checks from preceding labs.

## Capability additions

- tool registry
- file, test, Git CLI, Azure CLI, and shell tools registered as in Lab 2A
- canonical transcript IDs
- bounded tool loop
- built-in pre-tool command policy and pre-model history validation
- project hooks from `.harness/settings.json`: command `pre_tool` hooks can block
  a call (exit code 2); `post_tool` hooks can return feedback to the model
- path-scoped project rules from `.harness/rules/*.md`

Shell commands, destructive Git subcommands, and non-allowlisted Azure CLI calls
receive a paired denial result before execution. Project hooks can tighten but
not loosen the built-in policy. This educational policy is not an OS sandbox or a
substitute for human approval or isolation.
