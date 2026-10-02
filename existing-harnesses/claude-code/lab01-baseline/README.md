# Lab 1 — Constrained baseline vs the agent

**Start from:** `app/` at tag `lab00-done`, with the Lab 0 setup loaded
(see [Working in `app/`](../README.md#working-in-app)).

**Goal:** see what Claude Code adds on top of the model. You ask the same
questions with **all tools disabled** (`--tools ""`), which is the
closest a vendor CLI gets to a bare model call, and then with the default
tool set.

> Even with `--tools ""`, Claude Code still adds its own system prompt,
> environment details (working directory, OS, date, git status) and
> settings. Record this baseline as "constrained", not "bare".

## 1. A question that needs no tools (control)

```powershell
claude -p "What is the capital of India? One word." --tools ""
claude -p "What is the capital of India? One word."
```

Both should answer `New Delhi`. With or without tools, a pure knowledge
question costs about the same and behaves the same. This is your control.

## 2. A question about *this* project

```powershell
claude -p "What files are in this project and what does the README say it is for?" --tools ""
claude -p "What files are in this project and what does the README say it is for?"
```

```sh
claude -p "What files are in this project and what does the README say it is for?" --tools ""
claude -p "What files are in this project and what does the README say it is for?"
```

Compare:

- Without tools, the model can only guess. Does it admit that, or
  hallucinate files? It may still mention facts from the injected
  environment context (for example, that this is a git repo).
- With tools, it lists files and quotes `README.md`. To see the calls it
  made, re-run with `--output-format stream-json --verbose` and look for
  `"type":"tool_use"`. Or run `claude` interactively and ask the same
  question; the `⏺ Read(...)` lines are the tool loop you explore in
  Lab 2A.

## 3. A question that needs to execute something

```text
How many commits does this repository have, and what is the latest commit message?
```

Ask it both ways, as above. Only the tool-enabled run can run `git log`.
The constrained run either refuses or guesses.

## Record

| Prompt | Tools off: correct? | Tools on: correct? | Tools used |
|---|---|---|---|
| Capital of India | | | |
| Files / README | | | |
| Commit count | | | |

No files change in this lab. Tag it so the checkpoint sequence stays
continuous:

```powershell
git tag lab01-done
```
