# Lab 11 — Loop engineering

**Capability:** Codex has an internal agent loop. `--output-schema` constrains
the final response shape when the chosen model/provider supports it; it does
not implement a validated, bounded retry/poll/refinement scheduler for you.

Install Codex CLI; create a private temporary `CODEX_HOME`, copy this
lab's `config.toml.example` to `$CODEX_HOME/config.toml` and fill in
your endpoint, deployment and API version. Provide `AZURE_OPENAI_API_KEY`
through a fresh Entra token for `https://cognitiveservices.azure.com/` if
supported, or your own resource key from a secret manager; never save it
in files. From this lab directory, make a private disposable workspace:

```sh
workdir="$(mktemp -d)"
printf 'service: demo-order\nport: 3000\n' > "$workdir/service.txt"
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only \
  --output-schema service-map.schema.json \
  --output-last-message "$workdir/report.json" \
  "Read service.txt. Return a JSON service map. Cite service.txt:1-2 as evidence."
python -m json.tool "$workdir/report.json"
```

Run from this lab directory so `service-map.schema.json` resolves; if
`--output-schema` is unsupported by the Foundry deployment, mark this part
unavailable rather than asserting schema validity. Check that every
`name`, `port` and citation matches the source: a JSON shape constraint
does not validate facts.

For a bounded *manual* validation loop, if an answer is wrong, send the
specific errors through `codex exec resume --last "Correct only these
errors: ..."` and recheck. Stop on success, repeated identical errors, or
three attempts. Write down the exit reason. For retry, polling and
refinement, draw the trigger/evaluator/state change and all three exits;
do **not** execute side-effecting retries or unbounded polls against live
resources. This is a manual exercise, not a native programmable loop API.
