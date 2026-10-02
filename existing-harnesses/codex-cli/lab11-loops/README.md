# Lab 11 — Loop engineering

**Capability:** Codex has an internal agent loop. `--output-schema` constrains
the final response shape when the chosen model/provider supports it; it does
not implement a validated, bounded retry/poll/refinement scheduler for you.

Install Codex CLI; create a private temporary `CODEX_HOME`, copy this
lab's `config.toml.example` to `$CODEX_HOME/config.toml` and fill in
your endpoint (ending in `/openai/v1`) and deployment. Provide
`AZURE_OPENAI_API_KEY` through your resource key from a secret manager.
The [Microsoft guide](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/codex?tabs=npm)
says Entra ID is not supported for Codex; never save the key in files.
**Workspace:** start in `lab11-loops/` and follow the
[common preflight](../#workspace-and-preflight). Keep the schema in the
lab directory; only the generated report belongs in `workspace/`:

```powershell
"service: demo-order`nport: 3000" |
  Set-Content (Join-Path $workdir 'service.txt') -Encoding utf8
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only `
  --output-schema (Join-Path $labdir 'service-map.schema.json') `
  --output-last-message (Join-Path $workdir 'report.json') `
  "Read service.txt. Return a JSON service map. Cite service.txt:1-2 as evidence."
Get-Content (Join-Path $workdir 'report.json') -Raw | ConvertFrom-Json
```

```sh
printf 'service: demo-order\nport: 3000\n' > "$workdir/service.txt"
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only \
  --output-schema "$labdir/service-map.schema.json" \
  --output-last-message "$workdir/report.json" \
  "Read service.txt. Return a JSON service map. Cite service.txt:1-2 as evidence."
python -m json.tool "$workdir/report.json"
```

The schema path is absolute so changing working directories cannot break it; if
`--output-schema` is unsupported by the Foundry deployment, mark this part
unavailable rather than asserting schema validity. Check that every
`name`, `port` and citation matches the source: a JSON shape constraint
does not validate facts.

For a bounded *manual* validation loop, if an answer is wrong, send the
specific errors through `codex exec resume --last "Correct only these
errors: ..."` **from inside `workspace/`**, or pass the explicit session ID
from the first run, and recheck. Stop on success, repeated identical errors, or
three attempts. Write down the exit reason. For retry, polling and
refinement, draw the trigger/evaluator/state change and all three exits;
do **not** execute side-effecting retries or unbounded polls against live
resources. This is a manual exercise, not a native programmable loop API.

Follow [reset and cleanup](../#reset-and-cleanup) afterward.
