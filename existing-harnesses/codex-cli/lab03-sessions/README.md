# Lab 3 — History and sessions

**Capability:** Codex persists and resumes sessions. Its internal transcript
and crash replay rules are not the build-your-own JSONL contract.

Install Codex CLI; create a private temporary `CODEX_HOME`, copy this
lab's `config.toml.example` to `$CODEX_HOME/config.toml` and fill in
your endpoint (ending in `/openai/v1`) and deployment. Provide
`AZURE_OPENAI_API_KEY` from your resource key via a secret manager.
The [Microsoft guide](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/codex?tabs=npm)
says Entra ID is not supported for Codex. Do not save the key in files.
Run in a fresh, empty disposable directory (one session at a time):

```sh
workdir="$(mktemp -d)"
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only --json \
  "Remember this synthetic order queue name: orders-demo. Say only 'noted'."
codex exec resume --last --json \
  "What synthetic queue name did I give you? Do not guess if it is missing."
```

If your version's resume selection differs, pass the thread ID from the first
run's `thread.started` event to `codex exec resume <SESSION_ID>`. Verify that
the resumed answer uses prior context. Start a *new* `codex exec` session
with the same question and verify it does not inherit the previous thread.
Keep the two event streams private; they may include prompts and usage.

Record thread ID, whether resume worked, token usage if reported and whether
the provider also persists state. Do not claim the build-your-own guarantee
of replaying a crash between a tool call and its result: this lab does not
inject or validate that failure.
