# Lab 12 — Graph engineering

**Capability:** Codex has subagent parent/child relationships, not a
verified, user-facing declarative workflow graph CLI. Here the human
routes two questions to separate Codex runs; conditional edges, loop-back
and join semantics remain **outside** Codex.

Use the [preflight](../) with this lab's `config.toml.example`. Create a
disposable directory containing a service manifest and synthetic orders:

```sh
workdir="$(mktemp -d)"
printf 'demo-order: Go, port 3000, queue orders-demo\n' > "$workdir/service.txt"
printf 'product,status,total\nbowl,completed,20\nleash,completed,10\nbowl,pending,20\n' > "$workdir/orders.csv"
```

Route a **code question** to the retrieval action:

```sh
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only \
  "Read service.txt. Which queue does demo-order use? Cite the file."
```

Route a **data question** to the calculation action:

```sh
codex exec --skip-git-repo-check -C "$workdir" --sandbox read-only \
  "Using only orders.csv, calculate completed revenue by product in a markdown table. Show the rows included and excluded."
```

Verify the queue citation and the table totals (`bowl=20`, `leash=10`).
Now deliberately send the code question to the calculation action and
observe the wasted work. For an ambiguous request, **ask a human which
branch**; do not assert Codex provided a graph HITL node. Record routing
choice, calls, result and why each action was (or was not) needed.
Do not execute model-generated code on your host for this exercise; an
ACA-backed secure code-execution graph needs an external orchestrator
and is not provided by Codex CLI.
