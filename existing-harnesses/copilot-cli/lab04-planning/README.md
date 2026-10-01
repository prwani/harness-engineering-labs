# Lab 4 — Planning and todos

Use **this lab's** `provider.env.example` and the [preflight](../).
In a disposable workspace write `catalog.csv` with two synthetic
products, one priced zero. In interactive `copilot -C "$workdir"`,
request a numbered, read-only remediation plan. Inspect plan/todo
activity before proceeding. Compare a fresh session asked for the
same analysis without explicit planning. Count omitted issues and
tool calls where available. Only after reviewing the plan, authorize
edits to a *fresh copy* of synthetic data in a separate session;
inspect the actual diff. A plan is not an approval boundary and
Copilot's planner does not reproduce the build-your-own separate
agents, reminder hook or idempotency key contract.
