# Lab 2A — Tool loop

**Capability:** Codex already owns the tool loop and shell tool; you cannot
replace its call/result pairing with the build-your-own loop. Compare an
empty-workspace run to a run with a *synthetic* service manifest.

Install Codex CLI. Set `CODEX_HOME` to a private temporary directory,
copy this lab's `config.toml.example` to `$CODEX_HOME/config.toml`, and
replace the endpoint, deployment and API version. Set `AZURE_OPENAI_API_KEY`
to a fresh Entra token for `https://cognitiveservices.azure.com/` if
supported, or a learner-provided resource key via a secret manager.
Never save credentials in files. Make a disposable working directory
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
