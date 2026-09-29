# Lab 2B contract

- `lab.json` declares this snapshot's capabilities and resource-dependent live checks.
- `harness lab-info` renders the declaration without requiring cloud access.
- `pytest checks/` runs offline without Foundry, ACA, MCP servers, or telemetry resources.
- This folder is standalone and retains all checks from preceding labs.

## Capability additions

- tool registry
- Git CLI, Azure CLI, and shell tools registered as in Lab 2A
- canonical transcript IDs
- bounded tool loop
- pre-tool read-command policy and pre-model history validation

Shell commands and non-allowlisted CLI calls receive a paired denial result
before execution. This educational policy is not an OS sandbox or a substitute
for human approval or isolation.
