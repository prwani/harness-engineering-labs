# Lab 12 — Graph routing

Use this lab's `foundry.env.example` and the [preflight](../). In a
disposable workspace, add synthetic `service.txt` (demo-order
queue orders-demo) and `orders.csv` (completed bowl 20, completed
leash 10, pending bowl 20). Route “which queue?” and “revenue by
product for completed orders?” into separate read-only Claude Code
sessions. Verify queue `orders-demo` and totals `bowl=20`,
`leash=10` against the sources. For an ambiguous mixed request,
ask a human to choose the route before any tool use.

Document the intended router, state, branching and validation, and
which decisions were made manually. The CLI session and subagents
do not by themselves implement a durable typed graph, idempotent
nodes or replay. Do not call this a native graph run.
