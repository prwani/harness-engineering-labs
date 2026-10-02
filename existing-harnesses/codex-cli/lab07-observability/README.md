# Lab 7 — Observability and caching

**Capability:** Codex's `--json` emits a structured event stream and may
report token usage. It does not automatically provide the build-your-own
per-tool OTel span tree, approval decisions, or provider cache hit counters.

Install Codex CLI; create a private temporary `CODEX_HOME`, copy this
lab's `config.toml.example` to `$CODEX_HOME/config.toml` and fill in
your endpoint (ending in `/openai/v1`) and deployment. Set
`AZURE_OPENAI_API_KEY` from your resource key via a secret manager.
The [Microsoft guide](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/codex?tabs=npm)
says Entra ID is not supported for Codex; never save the key in files.
**Workspace:** start in `lab07-observability/` and follow the
[common preflight](../#workspace-and-preflight). Add the synthetic fixture:

```powershell
'demo-order: Go, port 3000, queue orders-demo' |
  Set-Content (Join-Path $workdir 'service.txt') -Encoding utf8
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only --json `
  "Read service.txt and report the port and queue with a file citation."
```

```sh
printf 'demo-order: Go, port 3000, queue orders-demo\n' > "$workdir/service.txt"
```

Run twice from separate fresh sessions with `codex exec --skip-git-repo-check
-C "$workdir" --sandbox read-only --json "Read service.txt and report the
port and queue with a file citation."`. Redirect stdout to **private files
outside the repository** if you want to inspect events side by side. Inspect
`thread.started`, item/tool events and `turn.completed` usage (if emitted).
Calculate tool call counts and compare total tokens and elapsed time; note
that warm-up and network variability can affect the difference. Remove
private traces when done.

Never publish the raw event stream: it may contain prompts, tool results
and sensitive data. Do not claim cache savings unless the provider reports
cached tokens for these runs. Mark per-call usage, cost, OTel spans and cache
counters unavailable if Codex does not expose them in your version.

Follow [reset and cleanup](../#reset-and-cleanup) afterward.
