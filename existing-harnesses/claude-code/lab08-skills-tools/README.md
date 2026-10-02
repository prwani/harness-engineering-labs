# Lab 8 — Skills and MCP tools

**Start from:** `app/` at tag `lab07-done`, with the Lab 0 setup loaded
(see [Working in `app/`](../README.md#working-in-app)).

**Goal:** extend the harness two ways:

- a **skill**: a packaged procedure (`SKILL.md`) that Claude loads only
  when it's relevant.
- an **MCP server**: an external process that offers new tools (here, a
  fake order system the app can't otherwise see).

## Part A: a release-notes skill

Read [`assets/.claude/skills/release-notes/SKILL.md`](assets/.claude/skills/release-notes/SKILL.md).
Only its `name` and `description` sit in context until it's used; the
body loads on demand. `allowed-tools` limits what it may run.

```powershell
Copy-Item -Recurse -Force ..\lab08-skills-tools\assets\* .
git add .claude ; git commit -m "chore: add release-notes skill"
```

```sh
cp -R ../lab08-skills-tools/assets/. .
git add .claude && git commit -m "chore: add release-notes skill"
```

Restart `claude`, then invoke it explicitly:

```text
/release-notes
```

…or implicitly, in a new session:

```text
What changed since tag lab04-done? Write it up as release notes.
```

**Observe:** the skill is picked up from its description, it runs `git
log` and groups commits by Conventional Commit type (your Lab 5
convention pays off here), and it updates `CHANGELOG.md` without
committing. Review and commit it yourself.

## Part B: an MCP server for orders

[`orders_mcp.py`](orders_mcp.py) is a ~100-line, dependency-free MCP
server over stdio. It exposes `list_orders(status)` and
`get_order(order_id)` with synthetic orders. Register it **for this
project only** (local scope), using an absolute path:

```powershell
claude mcp add orders -- python (Resolve-Path ..\lab08-skills-tools\orders_mcp.py).Path
claude mcp list
```

```sh
claude mcp add orders -- python "$(cd ../lab08-skills-tools && pwd)/orders_mcp.py"
claude mcp list
```

Start `claude`, run `/mcp` to see the server and its tools, then:

```text
Using the orders tools, find pending orders that we cannot fulfil with the current stock in catalog.csv. Write RESTOCK.md listing each SKU, quantity needed, stock on hand and shortfall.
```

**Observe:** tool calls named `mcp__orders__list_orders` /
`mcp__orders__get_order`, the approval prompt for a new tool, and how
Claude joins MCP data with local files. Check `RESTOCK.md` against
`catalog.csv` yourself. Did it correctly ignore the large **cancelled**
order?

When finished, unregister the server so it doesn't follow you into later
labs:

```powershell
claude mcp remove orders
```

## Record

- How the skill was triggered (slash command vs description match).
- The MCP tool names and whether you were asked to approve them.
- Anything in `RESTOCK.md` that was wrong.

## Checkpoint

Commit `CHANGELOG.md` and `RESTOCK.md` if you're keeping them:

```powershell
git tag lab08-done
```
