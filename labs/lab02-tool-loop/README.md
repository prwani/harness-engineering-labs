---
layout: default
title: "Lab 2A — Tool loop and unrestricted CLI tools"
---

# Lab 2A — Tool loop and unrestricted CLI tools

## Concept

This is where the harness stops being a single function call and becomes a
*loop*: the model declares intent ("call this tool with these arguments"),
the harness executes it, and the result is injected back — repeated until the
model stops or an iteration cap is hit. This lab also draws the line the
whole course is built on: the **harness** is the reusable runtime (loop,
tool execution). This first version deliberately exposes unrestricted command
execution so its behavior is easy to observe before later labs add hooks and
policy in Lab 2B.

**Key ideas**
- **Tool-call correlation is an invariant, not a nicety.** Every call gets
  exactly one result and IDs stay paired — Claude groups results into one
  message, GPT addresses them by `call_id`; the harness hides that difference.
- **Tools are host capabilities.** The model can request `git_cli`,
  `azure_cli`, or `shell`, but the harness owns the actual process execution
  and returns the command output to the model.
- **Unsafe by design.** These three tools accept arbitrary commands or
  arguments. This makes the initial demo direct and gives later hook and
  approval labs a concrete unsafe baseline to improve.
- **A hard iteration cap is the first stop condition.** More useful progress
  detection belongs in a later refinement of the loop.
- The repository helpers remain convenient for reads, but they are not a
  security boundary: unrestricted shell commands can read or modify anything
  available to the learner's operating-system account.

This self-contained snapshot starts from Lab 1 and introduces a first-cut,
offline-testable representation of its capability. It retains all earlier checks
and can be installed independently.

## Added in this lab

- [`harness/tool_loop.py`](harness/tool_loop.py) adds `run_tool_loop()`, which
  calls the model, dispatches named tools, pairs results with call IDs, and stops
  on a final turn or the iteration bound.
- [`harness/tools.py`](harness/tools.py) registers repository helpers plus
  unrestricted `git_cli`, `azure_cli`, and `shell` tools.

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

2. From a Git repository, open the persistent prompt:

   ```bash
   harness ask
   ```

   Ask `Use Git to show the current branch and working tree`, then ask
   `Use the shell to print the current directory`. Each tool call and
   `Assistant>` response appears above the reappearing `You>` prompt. Enter
   `/exit` to return to your shell. Questions are independent turns; session
   history is introduced in Lab 3. For a single question without entering the
   prompt, use `harness ask "Use Git to show the latest commit"`.

   The current directory is used by default. Use `--repo PATH` only when the
   tools should start in another working directory.

3. If you are already signed in to Azure CLI, ask the model to use it directly:

   ```bash
   az account show
   harness ask "Use Azure CLI to show the active account and list five visible resources"
   ```

   Azure CLI uses its existing login. No `--azure` switch is needed because
   `azure_cli` is always registered.

   > **Warning:** this lab is intentionally unrestricted. The model can run
   > mutating Git commands, mutating Azure commands, and arbitrary shell
   > commands with your user permissions. Use a disposable repository and
   > non-production Azure environment. Review each printed tool call. Do not
   > use this snapshot with untrusted prompts or content.
4. Run `pytest checks/test_tool_loop.py checks/test_tools.py checks/test_adapters.py`
   for deterministic offline verification, then `pytest checks/` for the full
   snapshot regression suite. These checks do not make a live model call.
5. Inspect the snapshot's declared capabilities with `harness lab-info`.

Continue with [Lab 2B](../lab02b-hooks/README.md) to add deterministic
`pre_tool` and `pre_model` hooks, deny unsafe commands before they execute,
and compare the paired tool results with this unrestricted baseline.

## External integrations

The direct interactive tool-loop exercise above requires a learner-provisioned
Foundry model. This snapshot does not include the automated evaluation suite:
- Foundry tool-call transcript

All live paths must use Entra credentials and must not add API-key configuration.
