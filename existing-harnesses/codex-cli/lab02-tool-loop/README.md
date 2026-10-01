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
Make a disposable working directory
containing only:

```sh
workdir="$(mktemp -d)"
printf 'service: order-service\nlanguage: Go\nport: 3000\ndepends_on: RabbitMQ\n' > "$workdir/service.txt"
```

Run in read-only mode (not unrestricted shell execution):

```sh
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only --json \
  "Report the service name, language, port and dependency from service.txt; cite the line numbers. Do not modify files."
```

Inspect the JSON events: find a tool invocation, its result and the final
answer; check the cited line against `service.txt`. Run again in an **empty**
workdir and note the difference in grounded answers. Report whether tools
were actually called. Do not use `danger-full-access` or disable approvals:
the build-your-own Lab 2A's deliberately unrestricted mode is *not* a safe
requirement for this path. Record any inaccessible internal loop details as
unavailable.
