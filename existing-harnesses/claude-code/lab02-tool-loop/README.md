# Lab 2A — The tool loop: build the app with files, shell, tests and git

**Start from:** `app/` at tag `lab01-done`, with the Lab 0 setup loaded
(see [Working in `app/`](../README.md#working-in-app)).

**Goal:** watch the agent loop (model → tool call → result → model …) do
real work. Claude Code writes files, runs the tests, reads the failures,
fixes them and uses git like a developer would. This is the same flow as
the [Claude Code quickstart](https://code.claude.com/docs/en/quickstart),
applied to the app you'll use for the rest of the course.

Start an interactive session in `app/`:

```powershell
claude
```

Claude Code asks before it edits files or runs commands. Read each request,
then approve it. Choosing "Yes, and don't ask again" for `python -m pytest`
is fine. Watch the `⏺` lines: each one is a tool call.

## 1. Build the app (Write + Bash + test-fix loop)

```text
Build a small Python pet-store order calculator in this folder. Use the standard library only, plus pytest for tests.
- catalog.csv with header sku,name,price_cents,stock and 5 synthetic products P1..P5 (prices in integer cents)
- inventory.py: load the catalog into a dict keyed by sku
- pricing.py: compute an order total in integer cents from (sku, qty) lines, with a tax rate in percent, rounding half up
- cli.py: `python cli.py total P1:2 P3:1` prints the total like $12.34
- tests/ with pytest tests for inventory and pricing, including a rounding edge case and a test that loads the real catalog.csv and checks every price and stock is a non-negative integer
Run the tests and fix any failures before you finish.
```

**Observe:** the files it creates (`Write`), the `python -m pytest`
command it runs, and whether it reads a failure and edits code again.
That retry *is* the loop. Count how many tool calls it took.

## 2. Use git as a tool

Ask these one at a time:

```text
What files have I changed?
```

```text
Commit the app with a descriptive conventional-commit message.
```

```text
Create a branch called feature/low-stock. On it, add a `python cli.py low-stock` command that lists products with stock below 5, with a test. Run the tests and commit.
```

```text
Show me the last 5 commits, then merge feature/low-stock into main.
```

**Observe:** Claude Code runs `git status`, `git diff`, `git switch -c`,
`git log` and `git merge` for you, and asks permission first. Check the
result yourself in a second terminal: `git log --oneline --graph`.

## 3. Debug a regression with git history

Exit Claude Code (`/exit`). Now *you* introduce a regression, the way a
careless teammate would, with a misleading commit message:

```powershell
(Get-Content catalog.csv) -replace '^P2,([^,]+),\d+,', 'P2,$1,12.99,' | Set-Content catalog.csv
git commit -am "docs: tidy catalog formatting"
```

```sh
sed -i.bak -E 's/^P2,([^,]+),[0-9]+,/P2,\1,12.99,/' catalog.csv && rm catalog.csv.bak
git commit -am "docs: tidy catalog formatting"
```

Start `claude` again and ask:

```text
The tests are failing on main. Use the git history to find which commit broke them and explain why, then fix it in a new commit. Do not rewrite history.
```

**Observe:** does it run the tests first, then `git log`/`git show`/`git
diff` (or even `git bisect`) to find the commit, instead of guessing? Does
it ignore the misleading "docs:" message and trust the diff?

## Record

- How many tool calls each step took and which tools (Write, Edit, Bash,
  Read, Grep …).
- Whether a test failure ever fed back into a fix without your prompting.
- One thing you would *not* have let it do without a prompt.

## Checkpoint

```powershell
python -m pytest -q
git status            # should be clean
git tag lab02a-done
```

Your app will differ from other learners'. That's fine, as long as tests
pass and `catalog.csv`, `pricing.py`, `inventory.py`, `cli.py` and
`tests/` exist, because later labs rely on those names.
