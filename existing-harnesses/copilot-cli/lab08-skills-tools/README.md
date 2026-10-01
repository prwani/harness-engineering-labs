# Lab 8 — Skills and MCP

Use **this lab's** `provider.env.example` and the [preflight](../).
In a disposable workspace put `product.txt` containing only a synthetic
name, material and use. Copy this lab's skill into
`"$workdir/.github/skills/product-description/SKILL.md"`. Run
`copilot skill list` or `/skills list` to verify discovery in a *fresh*
session, then ask for a description with and without this skill in
separate disposable workspaces. Verify claims against `product.txt`.
A skill is model-visible instructions, not a policy boundary; do not
put secrets or untrusted executables in its directory.

Inspect `copilot mcp --help` and `copilot mcp list`. If you have a
trusted, learner-controlled MCP server restricted to synthetic data,
add it in the isolated `COPILOT_HOME`, verify its tool list, run a
read-only request and remove it afterward. Do not enable built-in
GitHub MCP tools or connect production services merely to reach a
tool count. Mark MCP comparison not run if no trusted server is
available. Token tax needs actual usage and exposed tool lists; no
40-tool scaling or governance approval flow is claimed by this lab.
