# Lab 7 — Observability and usage

Use this lab's `foundry.env.example` and the [preflight](../). With a
synthetic `catalog.csv` in an isolated workspace, ask for a cited
anomaly and inspect `/cost` and the session transcript for any
available usage and tool-call details. Optionally inspect the CLI's
documented noninteractive JSON output in a **separate safe read-only
exercise**. Do not record credentials, full secret-bearing prompts
or files in logs.

Compare observed calls to the expected model → tool → answer sequence.
Record metrics that the CLI actually exposes; mark token, cache and
cost fields unavailable if not reported. CLI usage display is not
proof of a custom OpenTelemetry trace, redaction hook or equivalent
Foundry billing attribution.
