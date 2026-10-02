---
layout: default
title: "Lab 8 — Agent skills and tool scaling"
---

# Lab 8 — Agent skills and tool scaling

## Concept

Two different scaling problems, both about keeping context small as
capability grows: packaging a reusable *behavior* so it doesn't have to be
inlined every time (skills), and finding the right *tool* among dozens
without paying to describe all of them every call (tool search).

**Key ideas**
- **Skills vs. tools:** a tool is a function; a skill is a packaged,
  versioned behavior pattern (instructions + reference material + optional
  scripts) that an agent spec chooses to mount.
- **Progressive disclosure:** only a skill's name and description live in
  the system prompt; `load_skill(name)` pulls in the full body only when
  needed — the same pattern later powers on-demand tool loading.
- **Governance has teeth:** a skill must be published, then approved by a
  reviewer (hash recorded in `skills.lock`), and any edit requires a version
  bump and re-approval. An unapproved or tampered skill is refused at load
  time, not just discouraged.
- **The tool tax is real and measurable.** Mounting ~40 MCP tools inflates
  every call's token cost and increases wrong-tool selection. Exposing only
  `search_tools(query)` plus a small core set, with matches loaded on
  demand, cuts token cost by 5×+ with no accuracy loss — and loaded tools
  are appended, never reordered, so the Lab 7 cache prefix still survives.
- This is the other half of the **Lab 2B checkpoint**: one governed,
  mountable skill in production use.

This self-contained snapshot starts from Lab 7 and introduces a first-cut,
offline-testable representation of its capability. It retains all earlier checks
and can be installed independently.

## Added in this lab

- [`harness/skills.py`](harness/skills.py) adds `load_skill()` and
  `SkillRegistry` for parsing skill files and requiring approval before use.
- The same module adds `ToolCatalog` for tool discovery and
  `register_mcp_tools()` / `mcp_namespace()` for namespaced MCP metadata.

## Learner steps

1. Create and activate a virtual environment, then install the lab:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

2. Register a local tool and an MCP tool, then discover only the store server's
   tools:

   ```bash
   python - <<'PY'
   from harness.skills import ToolCatalog, register_mcp_tools

   catalog = ToolCatalog()
   catalog.register("read_file", "Read a repository file.")
   register_mcp_tools(catalog, "store", [{"name": "list_products", "description": "List products."}])
   for tool in catalog.discover(namespace="mcp:store"):
       print(tool.name, "-", tool.description)
   PY
   ```

   The discovered name is namespaced, so it cannot collide with `read_file`.
3. Run `pytest checks/test_skills.py` for deterministic verification, then
   `pytest checks/` for the full regression suite.
4. Inspect the snapshot's declared capabilities with `harness lab-info`.
5. Optional: to try the live Foundry prompt, copy `.env.example` to `.env`,
   fill in the endpoint and deployment settings, and sign in with `az login`.
   Run `harness ask` to ask repeated questions and type `/exit` to leave; use
   `harness ask "<question>"` for one-shot use. Each question is an independent
   turn; the Python example above exercises this lab's skills and tools.
   `ask` retains Lab 2B's file, test, repository and CLI tools behind the
   same hooks (shell and destructive Git denied; project hooks and rules
   from `.harness/` in the working directory), shows a spinner while it
   works, and ends each answer with the total time and a `Summary:` of
   LLM and tool calls.
   `--repo PATH` changes the tools' starting directory.

## External integrations

The following integration requires learner-provisioned credentials and resources;
this snapshot does not include a command to run it:
- MCP stdio integration

All live paths must use Entra credentials and must not add API-key configuration.
