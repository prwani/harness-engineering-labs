# Lab 1 — Constrained baseline

This independent exercise repeats the build-your-own Lab 1 **M1 task** using
Codex CLI. It cannot guarantee a bare call: Codex owns the agent loop and
read-only sandboxing does not disable all tools. Do not compare its results
as if the two harnesses had identical capabilities.

1. Start in `lab01-baseline/`. Install Codex CLI and check `codex exec --help`.
   Follow the [common preflight](../#workspace-and-preflight) for your shell
   to create a private home from **this lab's** config and set `workdir`
   to the tracked `workspace/`.

   Edit the copy to use your GPT Responses deployment and Azure OpenAI
   endpoint ending in `/openai/v1`. Load your own resource API key into
   `AZURE_OPENAI_API_KEY` via a secret manager; `env_key` names that
   environment variable, not a literal key. The
   [Microsoft Foundry guide](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/codex?tabs=npm)
   says Entra ID is not currently supported for Codex. Never store the
   key in files or logs. Create
   no fixtures: `workspace/` must contain only `.gitkeep`. Disable inherited
   project instructions with the option below. Do not configure a simulator,
   MCP servers or skills; this directory does not contain store evidence.

2. Run one fresh, noninteractive task with no prior session:

   ```powershell
   codex exec --skip-git-repo-check --sandbox read-only -C "$workdir" --json `
     -c project_doc_max_bytes=0 `
     "Produce a Store Health Report: (a) for each service, what it does, its language, port and dependencies; (b) every catalog issue (missing or weak descriptions, price anomalies, duplicates); (c) remediate the catalog issues. End with a StoreHealthReport JSON object with services, catalog_issues and remediations_claimed arrays. Cite file:line or product ID for each claim. Do not invent evidence or claim to have changed anything you could not access."
   ```

   ```sh
   codex exec --skip-git-repo-check --sandbox read-only -C "$workdir" --json \
     -c project_doc_max_bytes=0 \
     "Produce a Store Health Report: (a) for each service, what it does, its language, port and dependencies; (b) every catalog issue (missing or weak descriptions, price anomalies, duplicates); (c) remediate the catalog issues. End with a StoreHealthReport JSON object with services, catalog_issues and remediations_claimed arrays. Cite file:line or product ID for each claim. Do not invent evidence or claim to have changed anything you could not access."
   ```

   `--json` emits Codex's event stream. Inspect it for tool calls before
   describing the result as tool-free; do not treat a read-only sandbox as a
   tool-disable flag. The model cannot inspect the store or service source in
   this empty directory, so honest unknowns and no claimed fixes are expected.
   If it did access any external resources or tools, record that fact.

3. Record the Codex version, deployment, auth route (never the credential),
   whether tools were called, the report, and any usage Codex actually
   exposes. Mark unavailable metrics as unavailable, not zero. This pilot
   does **not** yet include a shared grader or claim a comparable scorecard.
   End the run, follow [cleanup](../#reset-and-cleanup) for the workspace and `CODEX_HOME`, and
   unset `AZURE_OPENAI_API_KEY`.

Next: introduce access to the same source and store simulator as the
build-your-own labs, with explicit permissions and measurable grading.
