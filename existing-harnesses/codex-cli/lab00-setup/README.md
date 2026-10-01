# Lab 0 — Configure Codex CLI for Foundry

Use a GPT deployment with the Responses API on Azure OpenAI in Microsoft
Foundry. Install the CLI as described in the
[Microsoft Foundry Codex guide](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/codex?tabs=npm):

```sh
npm install -g @openai/codex
codex --version
codex exec --help
```

1. Create a private, temporary Codex home and copy this lab's example:

   ```sh
   export CODEX_HOME="$(mktemp -d)"
   chmod 700 "$CODEX_HOME"
   cp config.toml.example "$CODEX_HOME/config.toml"
   ```

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

3. Smoke-test the provider from an empty directory:

   ```sh
   workdir="$(mktemp -d)"
   codex exec --skip-git-repo-check --sandbox read-only -C "$workdir" \
     "Say hello in one sentence."
   ```

   The command makes a live model request and may incur charges. Read-only
   restricts filesystem writes, **not** the agent loop or tool availability.
   If it fails, check the endpoint, deployment, credential and
   model support for Responses. The example is not a tested configuration
   for every Foundry resource.

4. When finished, remove the temporary work directory and `CODEX_HOME`
   (which may contain run history); unset `AZURE_OPENAI_API_KEY`. Do not print
   the environment variable or paste diagnostic logs containing credentials.

The [next lab](../lab01-baseline/) starts a constrained, but not genuinely
bare, agent run. For a stateless no-tools control, use the separate
build-your-own [Lab 1](../../../labs/lab01-bare-call/).
