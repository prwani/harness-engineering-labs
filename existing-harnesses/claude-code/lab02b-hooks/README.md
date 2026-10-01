# Lab 2B — Scoped rules and hooks

Use this lab's `foundry.env.example` and the [preflight](../). Copy
this lab's `.claude/rules/catalog.md` into the same relative path inside
a disposable workspace with synthetic `catalog.csv` and `service.txt`.
Inspect the `paths` frontmatter. Start a fresh Claude Code session,
ask for a cited catalog issue and then a service port, and check which
rule is included for each relevant file.

The scoped rule is contextual **instruction text**, not an executable
hook or a security policy. Inspect `/hooks` and the
[hook documentation](https://code.claude.com/docs/en/hooks) to identify
where a `PreToolUse` validation would run. Do not execute or install a
third-party hook in this exercise: hook commands run locally and their
exit behavior and trust must be reviewed independently. Compare a
model-followed instruction with an enforceable permission decision in
Lab 6; do not claim that a rule prevents unauthorized tool calls.
