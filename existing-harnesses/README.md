# Use an existing harness

This path explores the same capabilities as `labs/`, but configures a vendor
harness instead of building its loop. Start with [Codex CLI](codex-cli/);
[Codex SDK](codex-sdk/) has a separate directory for future exercises.

Each [CLI lab](codex-cli/) is an independent exercise across the complete
capability sequence, from [setup](codex-cli/lab00-setup/) and
[baseline](codex-cli/lab01-baseline/) to
[comparison](codex-cli/lab14-comparison/). These are not yet comparable
scored runs: Codex owns its loop and may expose built-in tools even in
read-only mode. Record which capabilities are built in, configurable or
unavailable instead of calling the baseline a bare model call. Advanced
workflow exercises explicitly identify any human-orchestrated step rather
than claiming Codex has a native graph runtime.

For Foundry, prefer Entra ID where the chosen harness and endpoint support it.
When they do not, a learner-provided API key is acceptable **in this path**.
Never commit keys or access tokens; the build-your-own `labs/` path retains its
Entra-only contract.
