# Lab 10 — Compaction

Use **this lab's** `provider.env.example` and the [preflight](../).
In a disposable workspace write two service files, with matching
publish/consume queue `orders-demo`. Start interactive Copilot,
summarize both files and use `/context` to inspect context usage.
Ask several follow-ups, then enter `/compact` inside the CLI,
not in your shell. Ask again for cited queue values and compare
to both files. Record what was retained and whether file reads
recurred. Note any usage or caching counters the provider exposes;
never infer cache hits from timing alone.

Compaction may discard details. It is not build-your-own Lab 10's
fixed-schema transcript rewrite or an unlimited context window.
