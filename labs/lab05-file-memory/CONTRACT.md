# Lab 5 contract

- `lab.json` declares this snapshot's capabilities and resource-dependent live checks.
- `harness lab-info` renders the declaration without requiring cloud access.
- `pytest checks/` runs offline without Foundry, ACA, MCP servers, or telemetry resources.
- This folder is standalone and retains all preceding Lab 0 checks.

## Capability additions

- session memory
- optimistic concurrency
- path scope enforcement
