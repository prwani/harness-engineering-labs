# Lab 11 — Bounded validation loop

Use this lab's `foundry.env.example` and the [preflight](../). Create
synthetic `catalog.csv` containing a zero-priced bowl and a normal
leash. Ask Claude Code to propose a correction, inspect the cited
row, and if you authorize a local edit, verify the diff and
recalculate the anomaly check. Repeat at most twice and stop if no
new evidence appears. Record each proposal, validation result and
stop reason.

This exercise is a **manual**, bounded validation loop. A prompt
requesting “retry until done” is not a deterministic stop hook,
retry budget or fail-closed policy. Do not use unattended tool
approval to emulate one.
