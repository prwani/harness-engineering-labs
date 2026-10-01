# Lab 1 — Constrained baseline

This independent exercise repeats the build-your-own Lab 1 **M1 task** using
Codex CLI. It cannot guarantee a bare call: Codex owns the agent loop and
read-only sandboxing does not disable all tools. Do not compare its results
as if the two harnesses had identical capabilities.

1. Install Codex CLI and check `codex exec --help`. Prepare an isolated home:

   ```sh
   export CODEX_HOME="$(mktemp -d)"
   chmod 700 "$CODEX_HOME"
   cp config.toml.example "$CODEX_HOME/config.toml"
   ```

   Edit the copy to use your GPT Responses deployment and Azure OpenAI
   endpoint ending in `/openai/v1`. For Entra ID, where accepted, run `az login`
   and acquire a token for this terminal session (renew it on expiry):

   ```sh
   export AZURE_OPENAI_API_KEY="$(az account get-access-token --resource https://cognitiveservices.azure.com/ --query accessToken -o tsv)"
   ```

   For resource-key auth, **replace** `env_key` in the config copy with
   `env_http_headers = { "api-key" = "AZURE_OPENAI_API_KEY" }`, then
   supply your key through the same environment variable via a secret
   manager. `env_key` uses the Authorization header and cannot be used with an
   Azure API key. Never store either credential in files or logs. Create
   a fresh, empty work directory. Do not mount a repository, simulator,
   MCP servers or skills.

2. Run one fresh, noninteractive task with no prior session:

   ```sh
   workdir="$(mktemp -d)"
   codex exec --skip-git-repo-check --sandbox read-only -C "$workdir" --json \
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
   End the run, remove the temporary work directory and `CODEX_HOME`, and
   unset `AZURE_OPENAI_API_KEY`.

Next: introduce access to the same source and store simulator as the
build-your-own labs, with explicit permissions and measurable grading.
