# Lab 4 — Planning and todos

**Capability:** Plan-then-execute can be requested of Codex; this does not
prove that its internal todo state is identical to the build-your-own
planner/executor and `write_todos` contract.

Install Codex CLI; create a private temporary `CODEX_HOME`, copy this
lab's `config.toml.example` to `$CODEX_HOME/config.toml` and fill in
the endpoint (ending in `/openai/v1`) and deployment. Set
`AZURE_OPENAI_API_KEY` to your resource key via a secret manager.
The [Microsoft guide](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/codex?tabs=npm)
says Entra ID is not supported for Codex; never save the key in files.
**Workspace:** start in `lab04-planning/` and follow the
[common preflight](../#workspace-and-preflight). Use `workspace/` for
planning and `workspace-b/` for the independent greedy comparison.
Create identical synthetic catalogs in both:

```powershell
$second = Join-Path $labdir 'workspace-b'
$catalog = '[{"id":1,"name":"Demo leash","price":0},{"id":2,"name":"Demo bowl","price":20}]'
$catalog | Set-Content (Join-Path $workdir 'catalog.json') -Encoding utf8
$catalog | Set-Content (Join-Path $second 'catalog.json') -Encoding utf8
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only --json `
  "Read catalog.json. First propose a numbered plan identifying questionable prices and the evidence for each; do not change any files."
```

```sh
second="$labdir/workspace-b"
printf '[{"id":1,"name":"Demo leash","price":0},{"id":2,"name":"Demo bowl","price":20}]\n' > "$workdir/catalog.json"
cp "$workdir/catalog.json" "$second/catalog.json"
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only --json \
  "Read catalog.json. First propose a numbered plan identifying questionable prices and the evidence for each; do not change any files."
```

Review the plan. In a *separate run* with a fresh copy of the catalog, ask
for an unplanned greedy analysis using `-C "$second"`; compare omitted
issues and tool usage. If you want to carry out a planned change, reset
`workspace-b/` and recreate its original catalog first,
use interactive `codex -C "$second" --sandbox workspace-write
--ask-for-approval on-request`, inspect each proposed change and approve only
explicitly authorized local edits. Do not connect a live store or assume
planning text is an enforcement boundary. Verify the catalog file and
record planned versus actual edits; mark unknown internal todo behavior as
unavailable.

Follow [reset and cleanup](../#reset-and-cleanup) after both passes.
