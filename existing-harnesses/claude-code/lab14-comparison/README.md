# Lab 14 — Cross-harness comparison

**Start from:** `app/` at tag `lab13-done`, with the Lab 0 setup loaded
(see [Working in `app/`](../README.md#working-in-app)).

**Goal:** run the **same task** under the same conditions in Claude Code,
another harness (the [Codex CLI track](../../codex-cli/)) and/or the
build-your-own harness from the main labs, then compare with measured
numbers rather than impressions.

## 1. Fix the task and the conditions

Use one well-specified task with an objective check:

```text
Add a `python cli.py export --format json` command that prints the catalog as a JSON array of objects with integer price_cents and stock. Add tests. Run the full test suite and stop only when it passes. Do not commit.
```

Keep these identical across harnesses, and write them down: starting
commit (`lab13-done`), model/deployment, instructions files
(`CLAUDE.md`/`AGENTS.md`), permissions (edits auto-accepted, pytest
allowed, no network, no push) and a budget/turn limit.

## 2. Run it in Claude Code

```powershell
$task = "Add a ``python cli.py export --format json`` command that prints the catalog as a JSON array of objects with integer price_cents and stock. Add tests. Run the full test suite and stop only when it passes. Do not commit."
git switch -c compare/claude lab13-done
claude -p $task --permission-mode acceptEdits --max-budget-usd 1 `
  --output-format stream-json --verbose --include-hook-events > .runs\lab14-claude.jsonl
python -m pytest -q
python ..\lab07-observability\analyze_stream.py .runs\lab14-claude.jsonl
git diff --stat lab13-done
```

Repeat once or twice if you can; one run is an anecdote.

## 3. Run it elsewhere

Check out a fresh branch from `lab13-done` for each other harness
(`git switch -c compare/codex lab13-done`), run the same prompt with that
harness's equivalent headless and permission settings, and capture its
own event log or usage output.

## 4. Compare

| Metric | Claude Code | Other harness | How measured |
|---|---|---|---|
| Tests pass at the end | | | `python -m pytest -q` |
| Files changed / lines | | | `git diff --stat lab13-done` |
| Turns | | | event stream |
| Tool calls (by type) | | | event stream |
| Input / output tokens | | | event stream |
| Cost estimate | | | harness-reported (list price) |
| Wall-clock time | | | event stream / stopwatch |
| Policy violations | | | denials, hooks, manual review |

And qualitatively: which capabilities were **built in**, **configured**
(settings, hooks, skills), **orchestrated by you** (scripts in Labs
11–13) or **unavailable**?

## Caveats

- Only compare numbers produced under matching conditions. Cost figures
  are each harness's own estimate, not your Azure bill.
- Claude Code has no truly bare-model mode; Lab 1's `--tools ""` is a
  constrained baseline. Don't equate it with the build-your-own harness's
  raw model call.
- Don't report scores you didn't observe.

## Checkpoint

Keep the branch whose result you prefer (or none), switch back to `main`:

```powershell
git switch main
git tag lab14-done
```
