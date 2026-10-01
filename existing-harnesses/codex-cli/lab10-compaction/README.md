# Lab 10 — Compaction and context management

**Capability:** Codex manages its own context and provides `/compact` in
interactive mode. It does not expose the build-your-own atomic
transcript-rewrite contract or guarantee that every fact survives.

Install Codex CLI; create a private temporary `CODEX_HOME`, copy this
lab's `config.toml.example` to `$CODEX_HOME/config.toml` and fill in
your endpoint (ending in `/openai/v1`) and deployment. Set
`AZURE_OPENAI_API_KEY` from a fresh Entra token for
`https://cognitiveservices.azure.com/` if supported. For a resource key,
replace `env_key` with `env_http_headers = { "api-key" = "AZURE_OPENAI_API_KEY" }`
in the copied config and load the key via a secret manager; never save it
in files. Create a fresh disposable directory containing:

```sh
workdir="$(mktemp -d)"
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
