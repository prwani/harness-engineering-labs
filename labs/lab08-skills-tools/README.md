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

- MCP stdio integration

All live paths must use Entra credentials and must not add API-key configuration.
