---
layout: default
title: "Lab 2B — Tool hooks and command policy"
---

# Lab 2B — Tool hooks and command policy

Lab 2A gave the model unrestricted `git_cli`, `azure_cli`, and `shell` tools.
This standalone snapshot retains those tool implementations but places
deterministic hooks in the execution path. The model still *requests* a tool;
the harness decides whether to execute it and always returns a result paired
with the model's call ID.

## What changes

- [`harness/hooks.py`](harness/hooks.py) implements a hook pipeline. `pre_model`
  validates the completed tool batches before every model call; `pre_tool`
  checks every requested call before execution.
- The built-in demonstration policy permits `git_cli` arguments `["status"]`
  or `["log", "-1", "--oneline"]`, and `azure_cli` arguments
  `["account", "show"]` or `["resource", "list"]`. It denies `shell` and
  other Git/Azure CLI arguments. Existing repository read helpers remain
  available.
- An additional hook can tighten the policy but cannot bypass the built-in
  hook. A denial returns `DENIED: <reason>` for the original call ID, and
  the CLI prints `Hook: denied ...`. Tool errors remain `ERROR: ...`.

## Try it

Create a virtual environment, install this lab independently, and configure
Foundry as in Lab 2A. On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e '.[dev]'
Copy-Item .env.example .env
az login
```

Fill in the non-secret Foundry endpoint and deployment settings in `.env`.
Start in a disposable Git repository:

```powershell
.\.venv\Scripts\harness.exe ask
```

Ask `Use git_cli with ["status"] to show the repository status`. Then ask
`Use shell to run "echo hello"` and inspect the printed hook denial. To
compare Azure behavior, ask the model to use `azure_cli` with
`["account", "show"]`, then with `["group", "delete", "--name", "demo"]`.
The latter must be **denied**; do not approve or run it yourself. The CLI
prints tool and hook events, but questions are independent turns until Lab 3.
`--repo PATH` optionally changes the tools' starting directory.

Run the deterministic checks without cloud access:

```powershell
.\.venv\Scripts\python.exe -m pytest checks\
.\.venv\Scripts\harness.exe lab-info
```

**Scope:** this is a teaching policy, not a sandbox. Allowed tools still run
with your local permissions. Git configuration, Azure CLI extensions, and
other runtime behavior are outside this small example policy. Do not use it
with untrusted input, production Azure resources, or sensitive repositories.
Lab 6 adds human approval as a distinct policy decision.

The already-published Labs 3 onward were created before this 2A/2B split and
have not yet inherited Lab 2B's hooks; do not treat those older snapshots as
an upgrade of this command policy.
