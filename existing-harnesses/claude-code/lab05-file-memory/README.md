# Lab 5 — File memory: CLAUDE.md

**Start from:** `app/` at tag `lab04-done`, with the Lab 0 setup loaded
(see [Working in `app/`](../README.md#working-in-app)).

**Goal:** give the harness durable project memory in a plain file that is
reviewed and versioned like code, and test when it is loaded and
followed.

## 1. Generate a starting CLAUDE.md

```powershell
claude
```

```text
/init
```

**Observe:** Claude explores the repo and writes `CLAUDE.md` (build/test
commands, architecture). Read it. Is anything wrong or invented?

## 2. Add your team's conventions

Open `CLAUDE.md` in your editor and add a section (keep it short; every
line costs context in every session):

```markdown
## Conventions
- Money is always integer cents. Never use float for prices or totals.
- Run `python -m pytest -q` and see it pass before saying a task is done.
- Commit messages follow Conventional Commits (feat:, fix:, docs:, chore:, test:).
- Never edit catalog.csv; catalog changes come from the warehouse sync.
```

Commit it: `git add CLAUDE.md; git commit -m "docs: add CLAUDE.md"`.

## 3. Fresh session: is the memory followed?

Exit and start a **new** session (`claude`, not `-c`), then:

```text
Add an optional gift-wrap fee of 299 cents per order, as a --gift-wrap flag on the total command. Commit when done.
```

**Observe, without reminding it:** integer cents? Tests run before "done"?
A `feat:` commit message? Run `/memory` to see which memory files were
loaded.

## 4. Edit memory mid-session

Without exiting, add a line to `CLAUDE.md` in your editor:

```markdown
- Every public function has a one-line docstring.
```

Then ask in the same session:

```text
Add a function that returns the most expensive product in the catalog.
```

**Observe:** did the new rule apply? Start a fresh session and ask again
for a comparison. Record when memory is (re)loaded in your version of
Claude Code.

## 5. Personal vs project memory

`CLAUDE.md` is shared with the team via git. For notes that only you
want, use `CLAUDE.local.md` (add it to `.gitignore`) or your user-level
`~/.claude/CLAUDE.md`. `/memory` shows which files are in effect.
Don't put secrets in any of them.

## Record

- Which conventions were followed unprompted, and which weren't.
- Whether a mid-session edit took effect.
- One thing that belongs in a hook (Lab 2B) rather than in memory, and why.

## Checkpoint

```powershell
python -m pytest -q ; git status
git tag lab05-done
```
