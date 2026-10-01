# Lab 3 — Sessions and resume

Use **this lab's** `provider.env.example` and the [preflight](../).
In an empty disposable workspace, start `copilot -C "$workdir" -i
"Remember the synthetic queue name orders-demo; say noted."`. Exit and
run `copilot -C "$workdir" --continue` in the same isolated
`COPILOT_HOME`; ask which queue was given. Compare to a *new*
session in the same workspace. Check `copilot sessions --help` or
`/session` for recorded session identifiers. Keep transcripts private.
This tests resumption, not atomic tool-result recovery, JSONL history
validation or exactly-once replay of mutating tools.
