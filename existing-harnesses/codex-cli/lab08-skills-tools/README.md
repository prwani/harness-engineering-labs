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
**Workspace:** start in `lab08-skills-tools/` and follow the
[common preflight](../#workspace-and-preflight). `workspace/` is the
**with-skill** run; `workspace-b/` is the **without-skill** run.
Reset both before setup so an old skill cannot contaminate the control.
Copy only **this lab's** skill, and create matching product fixtures:

```powershell
$second = Join-Path $labdir 'workspace-b'
$skilldir = Join-Path $workdir '.agents\skills\product-description'
New-Item -ItemType Directory -Path $skilldir -Force | Out-Null
Copy-Item .\product-description\SKILL.md $skilldir
'Demo bowl; material: ceramic; use: food.' |
  Set-Content (Join-Path $workdir 'product.txt') -Encoding utf8
Copy-Item (Join-Path $workdir 'product.txt') (Join-Path $second 'product.txt')
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only --json `
  "Use the product-description skill to describe product.txt. Cite product.txt."
```

```sh
second="$labdir/workspace-b"
mkdir -p "$workdir/.agents/skills/product-description"
cp product-description/SKILL.md "$workdir/.agents/skills/product-description/"
printf 'Demo bowl; material: ceramic; use: food.\n' > "$workdir/product.txt"
cp "$workdir/product.txt" "$second/product.txt"
```

Run `codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only
--json "Use the product-description skill to describe product.txt. Cite
product.txt."`. Compare a fresh `codex exec` run with `-C "$second"`
and the prompt `"Describe product.txt using only its attributes. Cite product.txt."`
(*without* installing a skill there) and check
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

For the altered-skill check, finish the no-skill run first, then reset
`workspace-b/`, recreate its product file and copy this lab's skill there
before editing and hashing it. Do not overwrite the original skill fixture.
Follow [reset and cleanup](../#reset-and-cleanup) afterward.
