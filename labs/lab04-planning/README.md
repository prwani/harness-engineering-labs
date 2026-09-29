---
layout: default
title: "Lab 4 — Planning and todos"
---

# Lab 4 — Planning and todos

## Concept

Up to now the agent has decided each next step greedily, one tool call at a
time. This lab separates **deciding what to do** from **doing it**, as two
agent specs sharing one harness: a `planner` (read-only tools plus
`write_todos`) and a `catalog-fixer` (write tools, works the plan). This
matters because this is also the lab where **write tools appear** —
`update_product`, `create_product`, and the irreversible `delete_product` —
and, deliberately, they are auto-approved for now. That gap is the whole
point of Lab 6.

**Key ideas**
- Todos are a first-class harness primitive, not a prompt convention: the
  harness owns the todo state and re-injects open todos every turn via a
  `pre_model` hook, so the agent can't "forget" the plan.
- Only the harness switches modes; an agent spec can't grant itself write
  tools it wasn't given.
- Plan-then-execute is compared directly against a greedy single-agent
  variant on the same task — expect fewer wasted/wrong writes and higher
  todo completion with planning.
- **Safe resume now covers writes:** every write carries an idempotency key,
  mutating calls run one at a time, and a crash between "applied" and
  "persisted" is reconciled against the simulator's write log on resume — no
  duplicate writes, ever.
- `unapproved_writes > 0` is *expected* here — it's the baseline number Lab 6
  drives to zero.

This self-contained snapshot starts from Lab 3 and introduces a first-cut,
offline-testable representation of its capability. It retains all earlier checks
and can be installed independently.

## Added in this lab

- [`harness/planning.py`](harness/planning.py) defines `AgentSpec`, the
  read-oriented `PLANNER` and write-capable `EXECUTOR` specs, and `ModeSwitch`;
  [`harness/cli/app.py`](harness/cli/app.py) exposes the `mode()` command.
- [`harness/todos.py`](harness/todos.py) adds `TodoList` for tracking open work
  and rendering a reminder.
- [`harness/writes.py`](harness/writes.py) adds `idempotency_key()`, `WriteLog`,
  and `run_write()` for reconciling repeated write calls.

## Learner steps

1. Create and activate a virtual environment, then install the lab:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

2. See the planner/executor boundary and harness-owned todos:

   ```bash
   python - <<'PY'
   from harness.planning import ModeSwitch
   from harness.todos import TodoList

   mode = ModeSwitch()
   print("Starting mode:", mode.mode, "tools:", mode.spec.tools)
   todos = TodoList()
   todos.write(["Inspect the service map", "Check configuration"])
   todos.complete("Inspect the service map")
   print(todos.reminder())
   print("Switched to:", mode.switch("execute").name)
   PY
   ```

   The planner starts read-only; the todo reminder keeps unfinished work
   visible when execution begins.
3. Run `pytest checks/test_planning.py` for deterministic verification, then
   `pytest checks/` for the full regression suite.
4. Inspect the snapshot's declared capabilities with `harness lab-info`.
5. Optional: to try the live Foundry prompt, copy `.env.example` to `.env`,
   fill in the endpoint and deployment settings, and sign in with `az login`.
   Run `harness ask` to ask repeated questions and type `/exit` to leave; use
   `harness ask "<question>"` for one-shot use. Each question is an independent
   turn; the Python example above exercises this lab's planning feature.

## External integrations

The following integration requires learner-provisioned credentials and resources;
this snapshot does not include a command to run it:
- Foundry catalog remediation

All live paths must use Entra credentials and must not add API-key configuration.
