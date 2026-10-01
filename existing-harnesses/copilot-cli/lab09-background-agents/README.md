# Lab 9 — Background agents and delegation

Use **this lab's** `provider.env.example` and the [preflight](../).
In a disposable directory put independent `order.txt` (port 3000,
publishes `orders-demo`) and `makeline.txt` (port 3001, consumes
`orders-demo`). Start interactive `copilot -C "$workdir"`; use
`/fleet` if supported to enable parallel subagents, and ask it to
delegate reading the two files independently. Request a final report
sorted by service name with citations. Inspect `/tasks` and the
session's child activity; if it did not spawn, report unavailable
instead of calling the run parallel.

In a fresh session ask for the same report without fleet; compare
actual wall time, provider-reported usage and citation correctness.
This is not an ACA sandbox, durable scheduler, deterministic merge
or tenant isolation guarantee. No child may write shared files.
