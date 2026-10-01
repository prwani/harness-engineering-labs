# Lab 5 — File-backed context and freshness

Use this lab's `foundry.env.example` and the [preflight](../). In a
disposable workspace add synthetic `service.txt` (port 3000) and
`catalog.csv` (bowl 20). Copy this lab's
`.claude/rules/service.md` to that same relative path inside the
workspace. Ask a fresh Claude Code session to cite the port; then
change the file to port 3001 and ask again. Check the file rather
than trusting previous session context. Compare a request about
`catalog.csv` to see whether the service-scoped rule is relevant.

Claude Code also reads project `CLAUDE.md` instructions when present.
These files and path-scoped rules are model context, not a versioned
database, access-control list or a guard against stale claims. The
`paths` field scopes instruction loading, not file permissions.
