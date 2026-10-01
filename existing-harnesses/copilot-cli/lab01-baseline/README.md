# Lab 1 — Constrained baseline

Use **this lab's** `provider.env.example` and the [preflight](../):
prepare an isolated `COPILOT_HOME`, set your chosen provider's credentials
securely, and create an empty disposable `workdir="$(mktemp -d)"`.

In interactive mode run `copilot -C "$workdir" -i "Produce a Store Health
Report: for each service identify name, language, port and dependencies;
list catalog issues and claimed remediations. Cite evidence for every
claim; report unknowns rather than guessing."`. Deny any unexpected
tool, URL or file access prompts. Do not enable auto-approval. Record
actual tool calls, known/unknown fields, version, deployment and usage
if shown. Neither an empty workspace nor denied access makes Copilot
a genuine stateless no-tools LLM call: the loop is built in and tool
availability depends on CLI configuration. This pilot is not a
scored run against the build-your-own answer key.
