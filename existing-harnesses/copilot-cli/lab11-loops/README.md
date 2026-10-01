# Lab 11 — Loop engineering

Use **this lab's** `provider.env.example` and the [preflight](../).
Create a synthetic `service.txt` with a name and port. In interactive
Copilot ask for JSON with `services` entries containing `name`,
`port` and `evidence` (`service.txt:line`). Check the output and each
citation against the file **outside the model**. If invalid, send
specific errors, not just "try again"; stop on success, repeated
identical errors, or three attempts. Record the exit reason.

Diagram how retry (transient failure), polling (finite deadline),
refinement (plateau) and validation (schema/citation) each need a
trigger, evaluator, state delta and bounded exits. Do not run
side-effecting retries or unlimited polling. Copilot's agent loop
does not itself prove an externally enforced `on_stop` validation
contract; this is a manual feedback loop unless separately implemented.
