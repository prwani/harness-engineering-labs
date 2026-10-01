# Lab 8 — Skills and MCP tool scaling

**Capability:** Codex can discover skills and register MCP servers. Skill
instructions are not an authorization policy; adding a server exposes tools
with the permissions of its process. Tool search and token-tax comparisons
require actual measured runs, not just a configured server list.

Install Codex CLI; create a private temporary `CODEX_HOME`, copy this
lab's `config.toml.example` to `$CODEX_HOME/config.toml` and fill in
the endpoint (ending in `/openai/v1`) and deployment. Provide
`AZURE_OPENAI_API_KEY` through your resource key from a secret manager.
The [Microsoft guide](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/codex?tabs=npm)
says Entra ID is not supported for Codex; never save the key in files.
Set up a disposable working directory containing a local,
reviewable skill:

```sh
workdir="$(mktemp -d)"
mkdir -p "$workdir/.agents/skills/product-description"
cp product-description/SKILL.md "$workdir/.agents/skills/product-description/"
printf 'Demo bowl; material: ceramic; use: food.\n' > "$workdir/product.txt"
```

Run `codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only
--json "Use the product-description skill to describe product.txt. Cite
product.txt."`. Compare to a fresh workspace *without* the skill and check
the responses against the actual attributes. Inspect the event stream or
Codex's skill listing in your installed version to confirm the skill was
loaded; a prompt alone does not prove it. Alter the skill body in a second
disposable copy and compare hashes before trusting a published skill.

Explore MCP safely with `codex mcp list` and `codex mcp add --help`. To
exercise tool discovery, register **only a trusted, learner-controlled MCP
server** restricted to synthetic data in this lab's isolated `CODEX_HOME`;
verify `codex mcp list --json`, run a read-only query, and remove it with
`codex mcp remove <name>`. Do not register production servers or pass a
Foundry credential to a third-party MCP process. If no trusted server is
available, mark the MCP portion **not run** rather than claiming a 40-tool
comparison. Contrast all-tools vs. a reduced set only when you can inspect
actual exposed tools and measure usage in both runs.
