# Lab 8 — Skills and MCP

Use this lab's `foundry.env.example` and the [preflight](../). In a
disposable workspace add a synthetic `product.txt` (bowl, ceramic,
pet feeding). Copy this lab's skill to
`.claude/skills/product-description/SKILL.md` in that workspace.
Start a fresh Claude Code session, inspect skill discovery and
compare descriptions generated with and without the skill in two
isolated workspaces. Check every claim against `product.txt`.

Inspect `/mcp` and `claude mcp --help`. Add an MCP server only if
you own a trusted, synthetic, read-only one; verify its tool list and
remove it after the exercise. Otherwise mark the MCP experiment not
run. Skill text is contextual instruction, and MCP servers are
external code/services; neither is a security boundary. Do not
connect production data just to increase tool count.
