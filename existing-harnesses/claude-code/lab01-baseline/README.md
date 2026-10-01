# Lab 1 — Constrained baseline

Use this lab's `foundry.env.example` and the [preflight](../). In an
isolated workspace with no repository instructions or MCP servers, add
synthetic `catalog.csv` with a zero-priced bowl and a leash priced 10.
Start an interactive Claude Code session and ask for a brief list of
suspect entries **without editing anything**. Inspect available tools
and the resulting transcript; check the source before accepting a claim.

Record model, prompt, response, tool calls, usage if exposed, and whether
any file changed. Claude Code retains its built-in loop and tools even
when the prompt requests no edits. This is a constrained agent baseline,
**not** a bare Messages API call. A prompt alone cannot sandbox tools.
