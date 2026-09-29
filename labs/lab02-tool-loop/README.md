---
layout: default
title: "Lab 2 — Tool loop and agent spec"
---

# Lab 2 — Tool loop and agent spec

## Concept

This is where the harness stops being a single function call and becomes a
*loop*: the model declares intent ("call this tool with these arguments"),
the harness executes it, and the result is injected back — repeated until the
model stops or an iteration cap is hit. This lab also draws the line the
whole course is built on: the **harness** is the reusable runtime (loop,
tool execution, hooks), and the **agent spec** is per-job configuration
(instructions, tool allow-list, model). The same harness will host many
different agents in later labs.

**Key ideas**
- **Tool-call correlation is an invariant, not a nicety.** Every call gets
  exactly one result, IDs stay paired, and `history.validate()` runs before
  every model call — Claude groups results into one message, GPT addresses
  them by `call_id`; the harness hides that difference.
- **Hooks, not more loop code.** `pre_tool` validates arguments and sandbox
  paths; `pre_model` validates history. Every later lab's cross-cutting
  behavior (approval, redaction, caching, compaction) is added the same way.
- **The agent spec is the seam.** Moving the system prompt, tool list, and
  model choice into `agents/store-ops.md` means swapping Claude for GPT is a
  one-line config change, not a code change.
- **Progress detection beyond a raw iteration cap:** duplicate-call
  suppression, a per-turn output budget, and stall detection (no *new*
  information served for 3 turns) stop a run that's spinning without
  actually running out of turns.
- With write tools still absent, accuracy on "diagnose" rises sharply over
  Lab 1's bare call — but "fix" stays at zero. That gap is next.

This self-contained snapshot starts from Lab 1 and introduces a first-cut,
offline-testable representation of its capability. It retains all earlier checks
and can be installed independently.

## Added in this lab

- [`harness/tool_loop.py`](harness/tool_loop.py) adds `run_tool_loop()`, which
  calls the model, dispatches named tools, pairs results with call IDs, and stops
  on a final turn or the iteration bound.

## Learner steps

1. Create and activate a virtual environment, install the lab, and configure
   the same non-secret Foundry settings used in Lab 0:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
az login
```

Set the endpoint and deployment values in `.env`; never put credentials or
API keys there. The local file and Git tools do not require Azure login.

2. From a Git repository, open the persistent prompt and ask questions that
   require looking at its files and recent history:

   ```bash
   harness ask --repo .
   ```

   Ask `Which top-level folders are here?`, then ask `What is the latest
   commit?`. Each tool call and `Assistant>` response appears above the
   reappearing `You>` prompt. Enter `/exit` to return to your shell. Questions
   are independent turns; session history is introduced in Lab 3. Tools are
   read-only and restricted to listing files, reading small files, Git status,
   and Git history; the harness does not expose arbitrary shell execution or
   writes. For a single question without entering the prompt, use
   `harness ask --repo . "What is the latest commit?"`.
3. If you are already signed in to Azure CLI, opt into read-only Azure tools:

   ```bash
   az account show
   harness ask --repo . --azure "Which Azure account is active and what resources can it see?"
   ```

   Azure CLI uses its existing login; `--azure` is required before these tools
   are made available. The command reports only the account name/tenant and
   up to 20 visible resources.
4. Run `pytest checks/test_tool_loop.py checks/test_tools.py checks/test_adapters.py`
   for deterministic offline verification, then `pytest checks/` for the full
   snapshot regression suite. These checks do not make a live model call.
5. Inspect the snapshot's declared capabilities with `harness lab-info`.

## External integrations

The direct interactive tool-loop exercise above requires a learner-provisioned
Foundry model. This snapshot does not include the automated evaluation suite:
- Foundry tool-call transcript

All live paths must use Entra credentials and must not add API-key configuration.
