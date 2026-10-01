# Lab 5 — File memory and scoped rules

Use **this lab's** `provider.env.example` and the [preflight](../).
In a disposable workspace create `service.txt` with a port and queue
and copy this lab's `.github/instructions/service.instructions.md`
into `"$workdir/.github/instructions/"`. Start fresh interactive
Copilot, inspect `/instructions`, then request cited facts from
`service.txt`. Record a scratch note in the workspace, exit, change
the service port and start a *new session* to compare note versus
source. Verify the current port yourself.

The `applyTo` rule controls when guidance enters context; it neither
restricts file access nor guarantees freshness. `--add-dir` grants
additional file access and trusts its config; avoid it here. Only OS
isolation and explicit permissions enforce path boundaries. This
exercise does not provide cross-session compare-and-swap or simulator
state versioning.
