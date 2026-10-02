# Lab 0 — Configure Codex CLI for Foundry

Use a GPT deployment with the Responses API on Azure OpenAI in Microsoft
Foundry. Install the CLI as described in the
[Microsoft Foundry Codex guide](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/codex?tabs=npm):

```sh
npm install -g @openai/codex
codex --version
codex exec --help
```

1. Start in `lab00-setup/`. Follow the [common preflight](../#workspace-and-preflight)
   to create a private temporary `CODEX_HOME`, copy **this lab's** example,
   and set `$workdir` (PowerShell) or `workdir` (bash) to this lab's
   tracked `workspace/`. No fixtures are needed; only `.gitkeep` is present.


   Edit `config.toml` in `CODEX_HOME`: set the deployment name and your
   resource's Azure OpenAI endpoint ending in `/openai/v1`. The v1
   Responses route does not need the preview `api-version` query parameter.
   Do not put credentials in this file or in the repository.

2. Supply your own Azure OpenAI resource API key through the
   `AZURE_OPENAI_API_KEY` environment variable, preferably via a secret
   manager. `env_key` in the example names the **variable**, not the secret
   value. Do not paste credentials into `config.toml`, shell history,
   `.env`, transcripts or commits. The linked Microsoft guide currently
   says **Entra ID is not supported for Codex**; do not use `az login` or
   an Entra token as a substitute for this key. This is an exception to
   the existing-harness path's "Entra wherever supported" preference.

3. Smoke-test the provider from the empty workspace:

   ```powershell
   codex exec --skip-git-repo-check --sandbox read-only -C "$workdir" `
     -c project_doc_max_bytes=0 "Say hello in one sentence."
   ```

   ```sh
   codex exec --skip-git-repo-check --sandbox read-only -C "$workdir" \
     -c project_doc_max_bytes=0 "Say hello in one sentence."
   ```

   The command makes a live model request and may incur charges. Read-only
   restricts filesystem writes, **not** the agent loop or tool availability.
   If it fails, check the endpoint, deployment, credential and
   model support for Responses. The example is not a tested configuration
   for every Foundry resource.

   **Native Windows:** complete the [Windows sandbox prerequisite](../#native-windows-prerequisite)
   in the same private `CODEX_HOME`, approving the administrator setup only
   if permitted on your machine. Then test an actual file read, not just
   model authentication:

   ```powershell
   'sandbox-check: 3000' |
     Set-Content (Join-Path $workdir 'sandbox-check.txt') -Encoding utf8
   codex exec --skip-git-repo-check --sandbox read-only -C "$workdir" --json `
     -c project_doc_max_bytes=0 `
     "Read sandbox-check.txt using a tool and quote its value with a file:line citation. Do not edit anything."
   ```

   The expected evidence is `sandbox-check.txt:1`, value `3000`, with a
   successful read in the event stream. If commands report `blocked by
   policy`, stop and resolve sandbox setup rather than treating the run as
   passed. Do not use full-access/bypass mode as a workaround.

4. When finished, follow [reset and cleanup](../#reset-and-cleanup) for the workspace and `CODEX_HOME`
   (which may contain run history); unset `AZURE_OPENAI_API_KEY`. Do not print
   the environment variable or paste diagnostic logs containing credentials.

The [next lab](../lab01-baseline/) starts a constrained, but not genuinely
bare, agent run. For a stateless no-tools control, use the separate
build-your-own [Lab 1](../../../labs/lab01-bare-call/).
