---
layout: default
title: "Lab 7 — Observability and prompt caching"
---

# Lab 7 — Observability and prompt caching

## Concept

Every prior lab has been flying blind on cost and latency. This lab turns
every model call, tool call, and hook decision into an OpenTelemetry span so
those questions have real answers — then uses the trace to find and fix the
two most expensive problems: wasteful reads and repeated failures.

**Key ideas**
- **Tracing must not change behavior.** The span tree (`agent.run` →
  `agent.iteration` → `gen_ai.chat` / `tool.execute`) and cost attribution
  per task/agent/tool are purely observational — a traced run scores the
  same as an untraced one.
- **The trace answers questions the model's own narration can't:** which
  step was most expensive (usually a full read of a large file), which step
  fails most often, and why a hook blocked or changed a call — all visible
  as span events.
- Input tokens grow roughly linearly per call and the run's total grows
  quadratically with turns, because the whole history is resent every time.
  This is the direct motivation for prompt caching in this lab and
  compaction in Lab 10.
- Each fix is its own flag, measured independently: tool-result size limits,
  retry-with-backoff on transient errors, always-on secret redaction, and
  prompt caching (ordering the prompt stable→volatile so the cache prefix
  survives).
- This is half of the **Lab 2B checkpoint**: spans on every step, the worst
  offenders identified and fixed.

This self-contained snapshot starts from Lab 6 and introduces a first-cut,
offline-testable representation of its capability. It retains all earlier checks
and can be installed independently.

## Added in this lab

- [`harness/telemetry.py`](harness/telemetry.py) adds `Span` and `Tracer` for
  recording a local span tree and `cost_for()` for usage-based cost estimates.
- The same module adds `redact()` for sensitive tool-output patterns and
  `cache_breakpoints()` for estimating stable prompt boundaries.

## Learner steps

1. Create and activate a virtual environment, then install the lab:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

2. Create a short trace, estimate usage cost, and inspect redaction:

   ```bash
   python - <<'PY'
   from harness.ledger import Usage
   from harness.telemetry import Tracer, cost_for, redact

   tracer = Tracer()
   run = tracer.start_run("inspect the catalog")
   run.child("tool.execute", tool="list_products").close()
   run.close()
   print([event["name"] for event in tracer.flatten()])
   print(f"Estimated cost: ${cost_for(Usage(input_tokens=1000, output_tokens=200), 'claude'):.4f}")
   print(redact('{"Authorization": "******"}'))
   PY
   ```

   The output shows the run/tool span tree, a usage-based estimate, and a
   redacted authorization value.
3. Run `pytest checks/test_telemetry.py` for deterministic verification, then
   `pytest checks/` for the full regression suite.
4. Inspect the snapshot's declared capabilities with `harness lab-info`.
5. Optional: to try the live Foundry prompt, copy `.env.example` to `.env`,
   fill in the endpoint and deployment settings, and sign in with `az login`.
   Run `harness ask` to ask repeated questions and type `/exit` to leave; use
   `harness ask "<question>"` for one-shot use. Each question is an independent
   turn; the Python example above exercises this lab's observability features.
   `ask` retains Lab 2B's file, test, repository and CLI tools behind the
   same hooks (shell and destructive Git denied; project hooks and rules
   from `.harness/` in the working directory), shows a spinner while it
   works, and ends each answer with the total time and a `Summary:` of
   LLM and tool calls.
   `--repo PATH` changes the tools' starting directory.

## External integrations

The following integrations require learner-provisioned credentials and resources;
this snapshot does not include commands to run them:
- Application Insights traces
- Foundry prompt cache probe

All live paths must use Entra credentials and must not add API-key configuration.
