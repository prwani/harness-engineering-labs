# Lab 13 — Planner, generator, evaluator

Use **this lab's** `provider.env.example` and the [preflight](../).
In a disposable workspace write `products.csv` with two synthetic
rows: ceramic Demo bowl for feeding and nylon Demo leash for walking.
Copy this lab's skill to
`"$workdir/.github/skills/product-description/SKILL.md"`.

1. In a new interactive session, request a read-only per-product
   plan; save the reviewed result to a scratch file in the workspace.
2. Start a **fresh generator** session. Request one description per
   product using the copied skill; save its response locally after
   checking it against the CSV.
3. Start a **fresh evaluator** session with only CSV and generated
   descriptions. Request a skeptical accuracy/brand score with
   evidence. Independently check invented attributes and errors.
4. Provide only concrete failures to a new generator run; at most
   two revisions, stop on no improvement. Compare to a fresh run
   without the skill and record usage when reported.

These are separate human-managed sessions/file handoffs. They do
not constitute an automatic dynamic graph, an objective grader or
approval for live catalog writes. Do not use real customer data.
