# Lab 10 — Compaction and context management

**Capability:** Codex manages its own context and provides `/compact` in
interactive mode. It does not expose the build-your-own atomic
transcript-rewrite contract or guarantee that every fact survives.

Install Codex CLI; create a private temporary `CODEX_HOME`, copy this
lab's `config.toml.example` to `$CODEX_HOME/config.toml` and fill in
your endpoint (ending in `/openai/v1`) and deployment. Set
`AZURE_OPENAI_API_KEY` from your resource key via a secret manager.
The [Microsoft guide](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/codex?tabs=npm)
says Entra ID is not supported for Codex; never save the key in files.
**Workspace:** start in `lab10-compaction/` and follow the
[common preflight](../#workspace-and-preflight). Add these synthetic files:

```powershell
'demo-order uses queue orders-demo' |
  Set-Content (Join-Path $workdir 'order.txt') -Encoding utf8
'demo-makeline consumes queue orders-demo' |
  Set-Content (Join-Path $workdir 'makeline.txt') -Encoding utf8
codex -C "$workdir" --sandbox read-only
```

```sh
printf 'demo-order uses queue orders-demo\n' > "$workdir/order.txt"
printf 'demo-makeline consumes queue orders-demo\n' > "$workdir/makeline.txt"
```

Start interactive `codex -C "$workdir" --sandbox read-only`.
Ask for both queue names with citations. Ask a few follow-up questions,
record the salient facts and context/usage indicators if shown by your
version, then enter `/compact` in the **interactive Codex prompt**, not in
your shell. Ask again which file supports each queue claim and compare
answers to the files. Continue by updating a synthetic fact in a fresh
workspace; verify it is reread instead of trusting a summary.

Record what was retained, dropped and re-fetched. If the model does not
support manual compaction in your version, mark the lab's manual step
unavailable. Do not claim a specific token threshold, saving percentage or
cache gain without provider measurements; compaction never removes the
model's hard context-window limit.

Follow [reset and cleanup](../#reset-and-cleanup) afterward.
