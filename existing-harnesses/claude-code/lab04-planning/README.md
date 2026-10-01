# Lab 4 — Plan before execution

Use this lab's `foundry.env.example` and the [preflight](../). In a
disposable workspace with synthetic `catalog.csv` and `service.txt`,
ask Claude Code to plan a catalog correction and a service-port check
before doing either. Enter plan mode interactively and inspect the
proposed steps, expected files, checks and approval points. Do not
approve edits yet. Then in a separate disposable copy, explicitly
authorize only a safe correction and verify the diff and port evidence.

Compare planned and actual actions. Plan mode belongs to the CLI and
is not an enforceable write policy, harness-owned todo store, or
idempotency guarantee. Stop on unexpected operations.
