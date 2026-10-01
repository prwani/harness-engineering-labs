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
Work only on a synthetic catalog in a new disposable directory:

```sh
workdir="$(mktemp -d)"
printf '[{"id":1,"name":"Demo leash","price":0},{"id":2,"name":"Demo bowl","price":20}]\n' > "$workdir/catalog.json"
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only --json \
  "Read catalog.json. First propose a numbered plan identifying questionable prices and the evidence for each; do not change any files."
```

Review the plan. In a *separate run* with a fresh copy of the catalog, ask
for an unplanned greedy analysis; compare omitted issues and tool usage.
If you want to carry out a planned change, create a fresh disposable copy,
use interactive `codex -C "$workdir" --sandbox workspace-write
--ask-for-approval on-request`, inspect each proposed change and approve only
explicitly authorized local edits. Do not connect a live store or assume
planning text is an enforcement boundary. Verify the catalog file and
record planned versus actual edits; mark unknown internal todo behavior as
unavailable.
