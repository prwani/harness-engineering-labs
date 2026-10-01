# Lab 9 — Background agents and delegation

**Capability:** Codex can delegate to child agents. A two-agent concurrency
cap bounds the example; it is not a claim of deterministic joins, tenant
isolation or ACA Sandboxes.

Install Codex CLI; create a private temporary `CODEX_HOME`, copy this
lab's `config.toml.example` to `$CODEX_HOME/config.toml` and fill in
the endpoint (ending in `/openai/v1`) and deployment. Provide
`AZURE_OPENAI_API_KEY` through your resource key from a secret manager.
The [Microsoft guide](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/codex?tabs=npm)
says Entra ID is not supported for Codex; never save the key in files.
Check `codex features list` for `multi_agent` before running.
Create a disposable, read-only workspace containing two independent files:

```sh
workdir="$(mktemp -d)"
printf 'name: demo-order\nport: 3000\nqueue: orders-demo\n' > "$workdir/order.txt"
printf 'name: demo-makeline\nport: 3001\nconsumes: orders-demo\n' > "$workdir/makeline.txt"
```

Run `codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only
--json "Delegate analysis of order.txt and makeline.txt to separate child
agents if supported; await both results and list each service's port and
queue with file citations, sorted by service name."`. Inspect collaboration
events to confirm spawning *actually happened*. Repeat in a new session
without delegation; compare wall time, reported tokens and completeness.
If the installed Codex version/model/provider does not spawn children,
report the feature unavailable rather than calling a single run parallel.

No children should write shared files. This exercise does not reproduce
the build-your-own scheduler, deterministic state merge, background
response polling or tenant-isolated sandbox lifecycle.
