# Lab 5 — File memory and access

**Capability:** Files can carry durable context between Codex sessions.
`AGENTS.md` provides repository instructions; it is not an optimistic-
concurrency memory store. File access is controlled by the sandbox and OS,
not by merely saying "do not read" in a prompt.

Install Codex CLI; create a private temporary `CODEX_HOME`, copy this
lab's `config.toml.example` to `$CODEX_HOME/config.toml` and fill in
your endpoint, deployment and API version. Set `AZURE_OPENAI_API_KEY` from
a fresh Entra token for `https://cognitiveservices.azure.com/` if supported,
or your own resource key from a secret manager; never save it in files.
Create a disposable workspace:

```sh
workdir="$(mktemp -d)"
printf 'service: demo-order\nport: 3000\n' > "$workdir/service.txt"
printf 'Synthetic training workspace. Cite service.txt for facts.\n' > "$workdir/AGENTS.md"
```

Run a read-only `codex exec --skip-git-repo-check -C "$workdir"
--sandbox read-only "Summarize service.txt with file:line citations."`.
Capture a note **outside the repo** in the disposable workspace; run a new
session and compare answers with and without that note. Change the port in
`service.txt` and verify Codex rereads it rather than trusting the old note.
Never copy secrets into context.

For a write-memory exercise, start interactive Codex with
`--sandbox workspace-write --ask-for-approval on-request` in the disposable
directory, request a note in `notes.md`, and inspect the resulting file
before resuming in a fresh session. Do not claim cross-session locking,
freshness keys or path-scoped `pre_tool` hooks unless you implemented and
tested them outside Codex. Clean up the workspace afterward.
