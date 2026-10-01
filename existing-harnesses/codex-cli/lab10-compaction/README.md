# Lab 10 — Compaction and context management

**Capability:** Codex manages its own context and provides `/compact` in
interactive mode. It does not expose the build-your-own atomic
transcript-rewrite contract or guarantee that every fact survives.

Use the [preflight](../) with this lab's `config.toml.example`, then start
interactive `codex -C "$workdir" --sandbox read-only` in a fresh disposable
directory containing:

```sh
workdir="$(mktemp -d)"
printf 'demo-order uses queue orders-demo\n' > "$workdir/order.txt"
printf 'demo-makeline consumes queue orders-demo\n' > "$workdir/makeline.txt"
```

Ask for both queue names with citations. Ask a few follow-up questions,
record the salient facts and context/usage indicators if shown by your
version, then enter `/compact` in the **interactive Codex prompt**, not in
your shell. Ask again which file supports each queue claim and compare
answers to the files. Continue by updating a synthetic fact in a fresh
workspace; verify it is reread instead of trusting a summary.

Record what was retained, dropped and re-fetched. If the model does not
support manual compaction in your version, mark the lab's manual step
unavailable. Do not claim a specific token threshold, saving percentage or
cache gain without provider measurements; compaction never removes the
model's hard context-window limit.
