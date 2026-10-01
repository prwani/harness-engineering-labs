# Lab 2A — Built-in tool loop

Use this lab's `foundry.env.example` and the [preflight](../). Put a
synthetic `catalog.csv` (one zero-priced bowl and one normal leash) and
`service.txt` (demo-order listens on port 3000) in a disposable
workspace. In an interactive session, ask Claude Code to locate the
suspect product and cite the service port. Inspect its file reads and
answers; compare them to the two sources. Then ask for a proposed price
correction, **not** an edit.

Record the requests, tool calls and terminal response. Claude Code
executes its own agent loop; this lab observes it rather than
implementing a tool registry, retries or a bare model adapter. Never
authorize unexpected shell or write actions.
