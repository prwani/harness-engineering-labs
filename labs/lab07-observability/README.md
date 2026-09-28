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

## Offline verification

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pytest checks/
harness lab-info
```

## Live validation (not run locally)

The following integrations require learner-provisioned credentials and resources:

- Application Insights traces
- Foundry prompt cache probe

All live paths must use Entra credentials and must not add API-key configuration.
