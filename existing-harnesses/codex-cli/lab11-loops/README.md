# Lab 11 — Loop engineering

**Capability:** Codex has an internal agent loop. `--output-schema` constrains
the final response shape when the chosen model/provider supports it; it does
not implement a validated, bounded retry/poll/refinement scheduler for you.

Use the [preflight](../) with this lab's `config.toml.example`. In a private,
disposable directory, make a synthetic service manifest:

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
