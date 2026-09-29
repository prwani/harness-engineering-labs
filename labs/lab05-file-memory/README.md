---
layout: default
title: "Lab 5 — File memory and access"
---

# Lab 5 — File memory and access

## Concept

Sessions (Lab 3) persist the *conversation*. This lab adds a place for the
agent to keep durable *artifacts* outside the transcript — notes, snapshots,
intermediate results — with governance rules for when that memory is shared
across sessions or agents.

**Key ideas**
- Session-scoped `memory/` (notes, snapshots) is on by default; a shared,
  cross-session store is opt-in per agent spec and can be read-only or
  read-write.
- **Optimistic concurrency:** a shared write fails if the file changed since
  it was read, so two writers can't silently clobber each other.
- File access is enforced the same way tool access is — a `pre_tool` hook
  denies any path outside the agent's granted scopes.
- **Freshness matters as much as persistence.** A cached artifact like
  `catalog_snapshot.json` is keyed by repo SHA and simulator state version;
  if the underlying state changed, the harness marks it stale rather than
  quietly reusing it.
- Net effect: a second run against unchanged state reuses the snapshot and
  makes fewer tool calls, but a state change (e.g. a price update) is
  detected and triggers a fresh read.
- What memory still *can't* do: keep irreversible writes safe (Lab 6), show
  where time and cost went (Lab 7), parallelize work (Lab 9), or stop context
  from growing (Lab 10).

This self-contained snapshot starts from Lab 4 and introduces a first-cut,
offline-testable representation of its capability. It retains all earlier checks
and can be installed independently.

## Added in this lab

- [`harness/memory.py`](harness/memory.py) adds `SessionMemory` for local files
  and `SharedStore` for opt-in, version-checked shared writes.
- The same module adds `FileScope.check()` for path authorization and
  `snapshot_key()` / `CachedArtifact.is_stale()` for freshness checks.
- [`harness/cli/app.py`](harness/cli/app.py) adds `memory_ls()` and
  `memory_show()` to inspect session-memory files.

## Learner steps

1. Create and activate a virtual environment, then install the lab:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

2. Run the focused test for this lab's memory behavior: `pytest checks/test_memory.py`.
   It uses deterministic fixtures, so it runs offline.
3. Run all checks for this snapshot and earlier labs: `pytest checks/`.
4. Inspect the snapshot's declared capabilities: `harness lab-info`.

## External integrations

The following integration requires learner-provisioned credentials and resources;
this snapshot does not include a command to run it:
- Foundry memory reuse evaluation

All live paths must use Entra credentials and must not add API-key configuration.
