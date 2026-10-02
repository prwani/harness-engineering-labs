# Lab 3 — Sessions: continue, resume, fork

**Start from:** `app/` at tag `lab02b-done`, with the Lab 0 setup loaded
(see [Working in `app/`](../README.md#working-in-app)).

**Goal:** a session is the conversation (messages, tool calls, results),
saved on disk by the harness. It is **not** a snapshot of your files. You
pause work, change the repo behind Claude's back, then continue, resume
and fork the conversation, and watch what it does and doesn't know.

## 1. Start a named session and investigate

```powershell
claude -n low-stock-threshold
```

```text
The low-stock threshold is hardcoded. Investigate how it's used and write NOTES.md with a short plan to make it configurable (CLI flag and/or environment variable). Don't change any code yet.
```

Exit with `/exit`. The session is saved under
`~/.claude/projects/<encoded-app-path>/`.

## 2. Change the repo while Claude isn't looking

In the same terminal, act as a teammate:

```powershell
git add NOTES.md ; git commit -m "docs: threshold notes"
(Get-Content catalog.csv) -replace '^(P4,[^,]+,\d+),\d+$', '${1},2' | Set-Content catalog.csv
git commit -am "chore: restock data from warehouse sync"
```

```sh
git add NOTES.md && git commit -m "docs: threshold notes"
sed -i.bak -E 's/^(P4,[^,]+,[0-9]+),[0-9]+$/\1,2/' catalog.csv && rm catalog.csv.bak
git commit -am "chore: restock data from warehouse sync"
```

## 3. Continue the most recent session

```powershell
claude -c
```

```text
Continue: implement the plan from NOTES.md, with tests. Before you start, tell me which products are currently low on stock.
```

**Observe:** the conversation is restored, so it remembers the plan
without re-reading everything. But does it trust its *memory* of
`catalog.csv` or re-read the file? Is P4 (stock now 2) in its list? A
restored session can hold stale facts about files that changed since.
Note whether it re-checks. Exit when the feature is done and tests pass;
commit it.

## 4. Resume by name, and fork an alternative

```powershell
claude --resume low-stock-threshold
```

`--resume` with a name or search term opens the session picker; with no
argument it lists recent sessions. Now **fork** that conversation, so you
can try a different design without polluting the original history:

```powershell
git switch -c try/env-only
claude --resume low-stock-threshold --fork-session
```

```text
Alternative design: drop the CLI flag and support only an environment variable LOW_STOCK_THRESHOLD. Implement it and run the tests.
```

Exit, and check the `/resume` picker: the original and the fork are
separate entries. Decide which design you prefer, then switch back to
`main` and delete the branch you're not keeping
(`git switch main; git branch -D try/env-only`).

## Record

- What `-c` restored, and whether stale file knowledge caused a mistake.
- How `--resume`, `-n/--name` and `--fork-session` differ.
- Where the session JSONL files live and roughly how big they are.

## Checkpoint

```powershell
git switch main ; python -m pytest -q
git tag lab03-done
```
