# Lab 14 — Compare harnesses

**Capability:** Native Codex provides a built-in loop, sandbox, sessions
and optional skills. The build-your-own control is a *true* bare call;
Codex's constrained baseline cannot be made equivalent merely by removing
project files or setting `--sandbox read-only`.

Install Codex CLI; create a private temporary `CODEX_HOME`, copy this
lab's `config.toml.example` to `$CODEX_HOME/config.toml` and fill in
your endpoint, deployment and API version. Provide `AZURE_OPENAI_API_KEY`
through a fresh Entra token for `https://cognitiveservices.azure.com/` if
supported, or your own resource key from a secret manager; never save it
in files. Run a fresh Codex session in an empty disposable directory:

```sh
workdir="$(mktemp -d)"
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only --json \
  "Produce a Store Health Report covering service name, language, port, dependencies and catalog issues. Return only supported evidence; do not claim any fixes without a write log."
```

For an *independent, comparable* run, have the build-your-own harness
and Codex work on the **same pinned source, seeded simulator state, task
prompt, output envelope and model deployment**, with the same allowed
tools, run count and grading rules. Do not read files from another lab
folder at runtime; export run results separately and compare them
afterward. This repository's Codex path does **not yet provide that
integration or scorer**. Until then, compare qualitative behavior only.

For each run record version, deployment, auth route (not credential),
tool access, sandbox policy, task, actual tool calls, evidence cited,
write log (if any), and provider-reported usage where exposed. Mark
missing metrics **unavailable**, never zero. Report which features were
built in, configurable, or unavailable; distinguish observed facts
from claims about equivalent scores.
