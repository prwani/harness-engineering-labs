# Lab 2A — Tool loop

**Capability:** Codex already owns the tool loop and shell tool; you cannot
replace its call/result pairing with the build-your-own loop. Compare an
empty-workspace run to a run with a *synthetic* service manifest.

Install Codex CLI. Set `CODEX_HOME` to a private temporary directory,
copy this lab's `config.toml.example` to `$CODEX_HOME/config.toml`, and
replace the endpoint (ending in `/openai/v1`) and deployment. Set
`AZURE_OPENAI_API_KEY` to your resource key via a secret manager. The
[Microsoft guide](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/codex?tabs=npm)
says Entra ID is not supported for Codex. Never save credentials in files.
**Workspace:** start in `lab02-tool-loop/` and follow the
[common preflight](../#workspace-and-preflight). It sets `workdir` to
this lab's `workspace/` and creates a private home from this lab's config.
Create the fixture (besides `.gitkeep`, this is the only input):

```powershell
"service: order-service`nlanguage: Go`nport: 3000`ndepends_on: RabbitMQ" |
  Set-Content (Join-Path $workdir 'service.txt') -Encoding utf8
```

```sh
printf 'service: order-service\nlanguage: Go\nport: 3000\ndepends_on: RabbitMQ\n' > "$workdir/service.txt"
```

Run in read-only mode (not unrestricted shell execution):

```powershell
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only --json `
  "Report the service name, language, port and dependency from service.txt; cite the line numbers. Do not modify files."
```

```sh
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only --json \
  "Report the service name, language, port and dependency from service.txt; cite the line numbers. Do not modify files."
```

Inspect the JSON events: find a tool invocation, its result and the final
answer; check the cited line against `service.txt`. Run again with `-C`
pointing to this lab's **empty** `workspace-b/` (only `.gitkeep`) and
`-c project_doc_max_bytes=0`, and note the difference in grounded answers.
For PowerShell, use `-C (Join-Path $labdir 'workspace-b')`; for bash,
use `-C "$labdir/workspace-b"`. Report whether tools
were actually called. Do not use `danger-full-access` or disable approvals:
the build-your-own Lab 2A's deliberately unrestricted mode is *not* a safe
requirement for this path. Record any inaccessible internal loop details as
unavailable.

Follow [reset and cleanup](../#reset-and-cleanup) after both runs.
