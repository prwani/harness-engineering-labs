# Lab 5 — File memory and access

**Capability:** Files can carry durable context between Codex sessions.
`AGENTS.md` provides repository instructions; it is not an optimistic-
concurrency memory store. File access is controlled by the sandbox and OS,
not by merely saying "do not read" in a prompt.

Install Codex CLI; create a private temporary `CODEX_HOME`, copy this
lab's `config.toml.example` to `$CODEX_HOME/config.toml` and fill in
your endpoint (ending in `/openai/v1`) and deployment. Set
`AZURE_OPENAI_API_KEY` from your resource key via a secret manager.
The [Microsoft guide](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/codex?tabs=npm)
says Entra ID is not supported for Codex; never save the key in files.
**Workspace:** start in `lab05-file-memory/` and follow the
[common preflight](../#workspace-and-preflight). Add these files to
this lab's `workspace/`:

```powershell
"service: demo-order`nport: 3000" |
  Set-Content (Join-Path $workdir 'service.txt') -Encoding utf8
'Synthetic training workspace. Cite service.txt for facts.' |
  Set-Content (Join-Path $workdir 'AGENTS.md') -Encoding utf8
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only `
  "Summarize service.txt with file:line citations."
```

```sh
printf 'service: demo-order\nport: 3000\n' > "$workdir/service.txt"
printf 'Synthetic training workspace. Cite service.txt for facts.\n' > "$workdir/AGENTS.md"
```

Run a read-only `codex exec --skip-git-repo-check -C "$workdir"
--sandbox read-only "Summarize service.txt with file:line citations."`.
Capture a note in the gitignored workspace; run a new
session and compare answers with and without that note. Change the port in
`service.txt` and verify Codex rereads it rather than trusting the old note.
Never copy secrets into context. The note now lives in the gitignored
workspace, not a tracked source file. Create it explicitly:

```powershell
'Previous observation: demo-order uses port 3000; reread service.txt.' |
  Set-Content (Join-Path $workdir 'notes.md') -Encoding utf8
```

```sh
printf 'Previous observation: demo-order uses port 3000; reread service.txt.\n' > "$workdir/notes.md"
```

First run a fresh session with the note and port 3000. Then change the port:

```powershell
"service: demo-order`nport: 3001" |
  Set-Content (Join-Path $workdir 'service.txt') -Encoding utf8
```

```sh
printf 'service: demo-order\nport: 3001\n' > "$workdir/service.txt"
```

Run another fresh session with the same question and verify 3001.

For a write-memory exercise, start interactive Codex with
`--sandbox workspace-write --ask-for-approval on-request` in the disposable
directory, request a note in `notes.md`, and inspect the resulting file
before resuming in a fresh session. Do not claim cross-session locking,
freshness keys or path-scoped `pre_tool` hooks unless you implemented and
tested them outside Codex. Follow [reset and cleanup](../#reset-and-cleanup)
afterward.
