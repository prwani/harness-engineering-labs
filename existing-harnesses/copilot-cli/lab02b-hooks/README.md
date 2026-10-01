# Lab 2B — Instruction rules, hooks and tool policy

Use **this lab's** `provider.env.example` and the [preflight](../).
Create a disposable workspace with `catalog.csv` and `service.txt`.
Copy this lab's `.github/instructions/catalog.instructions.md` into
`"$workdir/.github/instructions/"` and inspect the `applyTo` glob.
The rule is contextual *instruction text*, not an executable hook or
security policy. Copilot also supports `preToolUse` hooks; inspect the
[hook reference](https://docs.github.com/en/copilot/reference/hooks-reference)
to contrast lifecycle hooks with instructions. Hook timeouts may fall
through to normal permission handling, so do not claim fail-closed
enforcement. Start a **fresh** interactive `copilot -C "$workdir"`;
use `/instructions` to inspect loaded instruction sources. Ask for
a cited catalog issue, then a service port; compare which file-specific
rule appears to apply and what the model actually does. Stop if the
source is not loaded and inspect the CLI's trust/working-directory
configuration; do not assert enforcement based on model compliance.

For an enforced contrast, start another interactive session with
`copilot --deny-tool='shell(rm)' -C "$workdir"` and test only a harmless
read request. Use `copilot help permissions` to inspect the rule's match
semantics. A deny rule for `rm` does not prevent deletion by all tools,
nor does an instruction prevent a write. Denial takes precedence over
allow, and availability filters are different from approval permissions.
Never actually delete files for this drill. Lab 6 covers authorization
of writes; Lab 5 revisits path-scoped rules as contextual file guidance.
