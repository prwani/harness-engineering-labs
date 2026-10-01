# Lab 0 — Configure Claude Code with Foundry

Use this lab's `foundry.env.example` and the [common preflight](../).
Set `ANTHROPIC_FOUNDRY_RESOURCE` to your Foundry resource and source the
private copy outside the repository. With Entra, authenticate using
`az login` and verify access to the resource; otherwise supply
`ANTHROPIC_FOUNDRY_API_KEY` from a secret manager. Follow the
[Foundry Claude Code guide](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/configure-claude-code?tabs=bash)
for deployment, permission and model prerequisites.

Create a disposable workspace containing a synthetic `service.txt`
(demo-order, port 3000). Start `claude` inside that workspace and ask for
the port with a citation. Confirm that the selected model is the intended
Foundry deployment and record the authentication method without recording
the credential. Do not mistake a successful Azure CLI login for proof
that a live model request succeeded. Clean up workspace and environment
afterward.
