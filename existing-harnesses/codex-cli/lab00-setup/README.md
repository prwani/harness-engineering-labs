# Lab 0 — Configure Codex CLI for Foundry

Use a GPT deployment with the Responses API on Azure OpenAI in Microsoft
Foundry. Install the Codex CLI using the [official instructions](https://github.com/openai/codex).
Check `codex --version` and `codex exec --help` before continuing.

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

2. Choose **one** authentication route:

   - **Entra ID, if this endpoint accepts bearer tokens through Codex's
     `env_key` provider:** run `az login`, then set the variable for this
     terminal session:

     ```sh
     export AZURE_OPENAI_API_KEY="$(az account get-access-token --resource https://cognitiveservices.azure.com/ --query accessToken -o tsv)"
     ```

     Codex does not refresh this token for this provider. Renew it when it
     expires; if your deployment or Codex version does not accept it, use the
     key route instead. This variable name is a Codex provider setting, not
     a request to create an Azure API key.

   - **API key:** change the provider configuration: **remove**
     `env_key = "AZURE_OPENAI_API_KEY"` and put
     `env_http_headers = { "api-key" = "AZURE_OPENAI_API_KEY" }` in its
     place. Then supply your own resource key to `AZURE_OPENAI_API_KEY`
     using a secret manager or shell environment. Azure expects the
     `api-key` header for keys; Codex's `env_key` sends a **Bearer**
     header, suitable for Entra tokens, *not* Azure resource keys. Do not
     paste credentials into `config.toml`, shell history, `.env`,
     transcripts or commits.

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
