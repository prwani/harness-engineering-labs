# Lab 12 — Graph engineering

Use **this lab's** `provider.env.example` and the [preflight](../).
Create `service.txt` (demo-order, port 3000, queue orders-demo)
and `orders.csv` containing two completed orders (bowl 20 and
leash 10) and one pending bowl 20, all synthetic. Route the
code question (which queue?) and the data question (completed
revenue by product?) to separate interactive Copilot sessions
in the disposable workspace. Verify citations and expected
totals (`bowl=20`, `leash=10`), then try the wrong action and
record wasted work. For an ambiguous question ask a human to
choose the branch.

`copilot workflow run --help` exposes direct execution of a
**registered** dynamic workflow. This lab does not register a
workflow, so routing and loop-backs here are human-orchestrated,
not a tested native graph. If extending this into a production
graph, explicitly implement and test the router, bounded cycles,
idempotent nodes and isolated code executor; a prompt alone is
not an execution boundary.
