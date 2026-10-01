# Lab 3 — Session history and resume

Use this lab's `foundry.env.example` and the [preflight](../). Create
synthetic `catalog.csv` with a zero-priced bowl. Ask Claude Code in an
interactive session to identify the anomaly and cite its row. Exit,
change the synthetic bowl price to 20, and resume the session using
`claude --continue` from the **same workspace**. Ask for the current
price and verify it from the file, not from previous conversational
memory. Inspect `/resume` for explicit session selection.

Record where stale context misled an answer, if it did. Never resume a
session containing secrets. Session continuity does not guarantee
fresh file contents or recover arbitrary external side effects.
