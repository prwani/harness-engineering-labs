---
layout: default
title: "Lab 8 — Agent skills and tool scaling"
---

# Lab 8 — Agent skills and tool scaling

This standalone snapshot extends `harness ask` in two ways:

- a **skill**: a packaged procedure (`SKILL.md`) that the harness loads
  only when it's relevant.
- an **MCP server**: an external process that offers new tools. Here it is
  a fake order system the app can't otherwise see.

The exercise matches the
[Claude Code Lab 8](../../existing-harnesses/claude-code/lab08-skills-tools/).

## What changes

- [`harness/project_skills.py`](harness/project_skills.py):
  - Skills live in `.harness/skills/<name>/SKILL.md` in the project, or
    `~/.harness/skills/<name>/SKILL.md` for you alone. Front matter gives
    the `name`, a `description` and optional `allowed-tools`.
  - Only each skill's name and description go in the system prompt. The
    body is loaded on demand: by the model, with the `use_skill` tool, when
    a task matches the description; or by you, with `/<skill-name>
    [extra instructions]`.
  - `allowed-tools` lists permission rules (Lab 6 syntax) that are
    pre-approved once the skill is in use, so its routine steps run without
    prompts. They never override a deny or an explicit ask rule, and
    `/permissions` shows them.
- [`harness/mcp_client.py`](harness/mcp_client.py):
  - A minimal MCP client over stdio: start the server, `initialize`,
    `tools/list`, `tools/call`. Each server tool becomes
    `mcp__<server>__<tool>`, so it can't collide with a local tool.
  - MCP tools go through the same hooks, permissions and trace as local
    tools. A tool the rules don't mention **asks** (Lab 6 default).
  - `harness mcp add NAME -- COMMAND...` registers a server for **this
    project only**, in `~/.harness/projects/<project>/mcp.json` (outside
    the repository, like Claude Code's local scope). `harness mcp list`
    starts each server and lists its tools; `harness mcp remove NAME`
    unregisters it.
- [`orders_mcp.py`](orders_mcp.py) is a ~100-line, dependency-free MCP
  server with synthetic orders: `list_orders(status)` and
  `get_order(order_id)`.
- The CLI: `/skills` and `harness skills` list skills; `/mcp` lists servers
  and their tools.

[`harness/skills.py`](harness/skills.py) keeps the earlier in-process
models of a skill registry with approval state, tool discovery and MCP
namespacing.

## Learner steps

**Start from:** `labs/app/` at tag `lab07-done` (see the
[track guide](../README.md#working-in-labsapp)).

1. Install this lab and configure Foundry as before:

   ```bash
   python -m venv .venv
   . .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
   pip install -e '.[dev]'
   cp .env.example .env
   az login
   cd ../app
   ```

### Part A: a release-notes skill

2. Read
   [`assets/.harness/skills/release-notes/SKILL.md`](assets/.harness/skills/release-notes/SKILL.md),
   then install and commit it:

   ```bash
   cp -R ../lab08-skills-tools/assets/. .
   git add .harness && git commit -m "chore: add release-notes skill"
   harness skills
   ```

3. Invoke it explicitly:

   ```bash
   harness ask
   ```

   ```text
   /release-notes
   ```

   Then `/exit` and, in a **new** session, invoke it implicitly:

   ```bash
   harness ask "What changed since tag lab04-done? Write it up as release notes."
   ```

   **Observe:** in the second run, a `use_skill` tool call picked from the
   description. Then `git log` runs and `CHANGELOG.md` is written, although
   a one-shot run has no one to answer a permission prompt: the skill's
   `allowed-tools` pre-approved `write_file(CHANGELOG.md)`.
   Commits are grouped by Conventional Commit type (your Lab 5 convention
   pays off here). Nothing is committed. Review `CHANGELOG.md` and commit it
   yourself.

### Part B: an MCP server for orders

4. Register the server for this project, with an absolute path:

   ```bash
   harness mcp add orders -- python "$(cd ../lab08-skills-tools && pwd)/orders_mcp.py"
   harness mcp list
   ```

   ```powershell
   harness mcp add orders -- python (Resolve-Path ..\lab08-skills-tools\orders_mcp.py).Path
   harness mcp list
   ```

5. Use it:

   ```bash
   harness ask -n restock
   ```

   Type `/mcp` to see the server and its tools, then:

   ```text
   Using the orders tools, find pending orders that we cannot fulfil with the current stock in catalog.csv. Write RESTOCK.md listing each SKU, quantity needed, stock on hand and shortfall.
   ```

   **Observe:** tool calls named `mcp__orders__list_orders` /
   `mcp__orders__get_order`, the permission prompt for each new tool
   (answer `a` to allow the same call for the session), and how the model
   joins MCP data with local files. Check `RESTOCK.md` against
   `catalog.csv` yourself. Did it correctly ignore the large **cancelled**
   order?

6. Unregister the server so it doesn't follow you into later labs:

   ```bash
   harness mcp remove orders
   ```

7. **Record**
   - How the skill was triggered (slash command vs description match), and
     which calls its `allowed-tools` let through without a prompt.
   - The MCP tool names and whether you were asked to approve them.
   - Anything in `RESTOCK.md` that was wrong.

8. **Checkpoint.** Commit `CHANGELOG.md` and `RESTOCK.md` if you're keeping
   them, then in `app/`:

   ```bash
   git tag lab08-done
   ```

9. Back in the lab folder, run the offline checks and inspect the declared
   capabilities:

   ```bash
   pytest checks/
   harness lab-info
   ```

`harness ask` keeps tracing (Lab 7), permissions (Lab 6), file memory
(Lab 5), plan mode and todos (Lab 4), sessions (Lab 3) and the Lab 2B
tools, built-in policy, project hooks and rules. This is a teaching
harness, not a sandbox: only use it on the practice app.
