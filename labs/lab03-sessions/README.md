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

## Learner steps

1. Create and activate a virtual environment, then install the lab:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

2. Experience persistence and resume with a small user/assistant exchange:

   ```bash
   python - <<'PY'
   from pathlib import Path
   from tempfile import TemporaryDirectory
   from harness.session import Session

   with TemporaryDirectory() as directory:
       path = Path(directory) / "session.jsonl"
       session = Session()
       session.append({"role": "user", "content": "List the services"}, path)
       session.append({"role": "assistant", "content": "I found 8 services."}, path)
       resumed = Session.resume(path)
       print(resumed.session_id, resumed.messages[-1]["content"])
   PY
   ```

   The output shows the same session ID and the last persisted answer.
3. Run `pytest checks/test_session.py` for deterministic verification, then
   `pytest checks/` for the full regression suite.
4. Inspect the snapshot's declared capabilities with `harness lab-info`.
5. Optional: to try the live Foundry prompt, copy `.env.example` to `.env`,
   fill in the endpoint and deployment settings, and sign in with `az login`.
   Run `harness ask` to ask repeated questions and type `/exit` to leave; use
   `harness ask "<question>"` for one-shot use. Each question is an independent
   turn; the Python example above demonstrates this lab's session persistence.
   `ask` retains Lab 2B's repository and CLI tools behind the same
   `pre_tool`/`pre_model` hooks (shell denied; Git and Azure CLI limited to
   a few read commands), shows a spinner while it works, and ends each
   answer with the total time and a `Summary:` of LLM and tool calls.
   `--repo PATH` changes the tools' starting directory.

## External integrations

The following integration requires learner-provisioned credentials and resources;
this snapshot does not include a command to run it:
- Foundry resumed-session evaluation

All live paths must use Entra credentials and must not add API-key configuration.
