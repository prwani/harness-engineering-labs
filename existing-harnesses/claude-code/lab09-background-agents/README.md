# Lab 9 — Delegation and background agents

Use this lab's `foundry.env.example` and the [preflight](../). Put
synthetic `catalog.csv` (zero-priced bowl) and `service.txt`
(demo-order port 3000) in an isolated workspace. Ask Claude Code to
delegate two independent read-only investigations to subagents and
return a short cited synthesis. Observe the task/subagent controls
available in your installed version; do not assume background
execution is enabled by default. Check whether separate subagent
contexts preserve both sets of source citations.

Record parent/child boundaries and which work, if any, actually ran
concurrently. Do not share credentials or writable production files
with child processes. Native delegation is not the build-your-own
harness's persistent background-agent registry or fan-out contract.
