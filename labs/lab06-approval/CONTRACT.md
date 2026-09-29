# Lab 6 contract

- `lab.json` declares this snapshot's capabilities and resource-dependent live checks.
- `harness lab-info` renders the declaration without requiring cloud access.
- `pytest checks/` runs offline without Foundry, ACA, MCP servers, or telemetry resources.
- This folder is standalone and retains all checks from preceding labs.

## Capability additions

- tool policy gate
- standing approvals
- write audit log

`harness ask` retains the Lab 2B tool loop: repository and CLI tools run
behind the pre-tool command policy and pre-model history validation, and
each answer reports elapsed time plus LLM/tool call counts.
