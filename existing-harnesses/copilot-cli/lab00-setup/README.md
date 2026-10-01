# Lab 0 — Configure GitHub Copilot CLI

Install `@github/copilot` via the [official CLI instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli).
Run `copilot --version` and `copilot help providers`.

To use a Foundry GPT Responses deployment, create an isolated
`COPILOT_HOME`, copy **this lab's** `provider.env.example` to a private
temporary file outside the repository, replace the resource host and
deployment name, and source it. Set `COPILOT_PROVIDER_MODEL_ID` to a
well-known base model ID supported by your CLI and
`COPILOT_PROVIDER_WIRE_MODEL` to your Foundry deployment name. Set
`COPILOT_MODEL` to the configured model selection, and
`COPILOT_PROVIDER_AZURE_API_VERSION` to the version required by your
endpoint. Provide `COPILOT_PROVIDER_API_KEY` securely. An Entra bearer
token is not part of the documented Azure BYOK recipe; only attempt
it after independently validating your endpoint and CLI version.
Set only one credential source.
BYOK does not require GitHub sign-in. Do not commit keys/tokens or capture
them in debug logs.

Remote Foundry deployment compatibility is not established merely by
setting these variables: test authentication, streaming and tool calling
on your deployment and record any unsupported combinations.

If you instead choose the hosted Copilot path, **do not source the BYOK
variables**; run `copilot login` and select a model your account can use.
This is not a Foundry run and must be labeled accordingly.

In a disposable directory run `copilot -C "$workdir" -i "Say hello in one
sentence."` (create it first with `workdir="$(mktemp -d)"`). Inspect the
provider and model selected. The CLI may expose built-in tools even for
this prompt; do not call it a bare model request. Remove temporary
workspace, config and `COPILOT_HOME` after the exercise and unset
credential variables. See [provider reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)
and `copilot help providers` for version-specific provider behavior.
