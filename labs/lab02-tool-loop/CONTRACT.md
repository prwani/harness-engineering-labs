# Lab 2A contract

- `lab.json` declares this snapshot's capabilities and resource-dependent live checks.
- `harness lab-info` renders the declaration without requiring cloud access.
- `pytest checks/` runs offline without Foundry, ACA, MCP servers, or telemetry resources.
- This folder is standalone and retains all checks from preceding labs.

## Capability additions

- tool registry
- `write_file`, `edit_file`, and `run_tests` tools rooted in the working directory
- unrestricted Git CLI, Azure CLI, and shell tools
- canonical transcript IDs
- bounded tool loop

This snapshot is intentionally unsafe: CLI tools run with the learner's local
permissions and do not yet pass through restriction or approval hooks.
