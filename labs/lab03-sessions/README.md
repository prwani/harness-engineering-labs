---
layout: default
title: "Lab 3 — History and sessions"
---

# Lab 3 — History and sessions

## Concept

A tool loop (Lab 2) only remembers what happened *within* one run. This lab
gives the harness durable memory of the run itself: every model call and
tool result is appended to a session log as it happens, so a run can be
resumed after a crash instead of restarted from scratch.

**Key ideas**
- A `Session` bundles the transcript, the agent spec's hash, and the fixed
  provider for that run — nothing about a run's identity is allowed to
  drift mid-session.
- Persistence happens after *every* step, not at the end, so `harness
  resume <id>` can continue from the last completed step.
- Crash recovery has a rule: a read-only tool call with no persisted result
  is safely re-executed on resume; nothing is silently dropped or duplicated.
- Printing tokens per call surfaces a problem this lab doesn't yet solve:
  re-sending the whole history each turn makes context grow with every step.
  That growth is what Lab 10 (compaction) exists to fix.
- A resumed run reaches the same final report as an uninterrupted one, using
  fewer total tokens than starting over — durability is a cost win, not just
  a safety net.

This self-contained snapshot starts from Lab 2 and introduces a first-cut,
offline-testable representation of its capability. It retains all earlier checks
and can be installed independently.

## Added in this lab

- [`harness/session.py`](harness/session.py) adds `Session.append()` for a
  JSONL-backed message history and `Session.resume()` to reconstruct it while
  checking that all entries belong to the same session.

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

- Foundry resumed-session evaluation

All live paths must use Entra credentials and must not add API-key configuration.
