# Use an existing harness

This path explores the same capabilities as `labs/`, but configures a vendor
harness instead of building its loop. Choose [Codex CLI](codex-cli/),
[Claude Code](claude-code/) or [GitHub Copilot CLI](copilot-cli/).
[Codex SDK](codex-sdk/) has a separate directory for future exercises.

Each CLI lab is an independent exercise across the complete
capability sequence, from [setup](codex-cli/lab00-setup/) and
[baseline](codex-cli/lab01-baseline/) to
[comparison](codex-cli/lab14-comparison/), with corresponding standalone
folders for the other CLIs. These are not yet comparable scored runs:
vendor CLIs own their loop and may expose built-in tools even in
read-only mode. Record which capabilities are built in, configurable or
unavailable instead of calling the baseline a bare model call. Advanced
workflow exercises identify human-orchestrated steps rather than
claiming a native graph runtime.

For Foundry, prefer Entra ID where the chosen harness and endpoint support it.
The [Codex CLI guide](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/codex?tabs=npm)
currently says Entra ID is not supported for Codex; its exercises use
a learner-provided resource API key. The
[Claude Code guide](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/configure-claude-code?tabs=bash)
documents both Entra and key authentication. Copilot CLI's documented
Azure BYOK example uses an API key; do not confuse the Foundry resource
management skill with inference authentication. Scoped instruction
rules appear in CLI Labs 2B and 5; Lab 6 contrasts them with tool
permissions and approval.
Never commit keys or access tokens; the build-your-own `labs/` path retains its
Entra-only contract.
