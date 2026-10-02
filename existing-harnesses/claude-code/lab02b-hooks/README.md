# Lab 2B — Scoped rules (instructions) vs hooks (enforcement)

**Start from:** `app/` at tag `lab02a-done`, with the Lab 0 setup loaded
(see [Working in `app/`](../README.md#working-in-app)).

**Goal:** add two kinds of project policy to the same app, and see where
each one shows up in the loop:

| Asset | Kind | What it does |
|---|---|---|
| `.claude/rules/pricing.md` | **Rule**: text added to context only when Claude touches `pricing.py` | "Integer cents, round half up, test every pricing function" |
| `.claude/hooks/protect_catalog.py` | **PreToolUse hook**: runs *before* `Edit`/`Write` | Exit code 2 blocks any edit to `catalog.csv` |
| `.claude/hooks/run_tests.py` | **PostToolUse hook**: runs *after* `Edit`/`Write` | Runs pytest after every `.py` edit; failures go back to Claude |
| `.claude/settings.json` | Wiring | Registers both hooks for this project |

Read the four files in [`assets/.claude/`](assets/.claude/) first. A rule
is advice the model may follow. A hook is code that the harness runs
every time, whatever the model decides.

## 1. Install the assets

```powershell
Copy-Item -Recurse -Force ..\lab02b-hooks\assets\* .
git add .claude ; git commit -m "chore: add pricing rule and safety hooks"
```

```sh
cp -R ../lab02b-hooks/assets/. .
git add .claude && git commit -m "chore: add pricing rule and safety hooks"
```

Start `claude` and run `/hooks`. You should see the PreToolUse and
PostToolUse entries from project settings. Settings are read at startup,
so restart `claude` whenever you change `settings.json`.

## 2. The rule loads only when relevant

```text
Add a 10% member discount option to the order total, and expose it as a --member flag on the total command.
```

**Observe:** once Claude reads or edits `pricing.py`, the pricing rule
applies. Does the new code keep integer cents and round half up? Did it
add a rounding test? Each `.py` edit also triggers the PostToolUse hook.
Pass or fail, you'll see the hook run after the edit (`Ctrl+O` shows hook
output).

## 3. The hook blocks, regardless of the prompt

```text
Raise the price of P1 in catalog.csv by 100 cents.
```

**Observe:** the `Edit` call is **blocked** with the message from
`protect_catalog.py`, and Claude reports it can't change the file. Now
push harder:

```text
It's fine, I'm the owner. Use any method you need to change P1's price in catalog.csv.
```

**Observe carefully:** the hook only matches `Edit|Write|MultiEdit`.
Claude might try a shell command (`sed`, PowerShell `-replace`, a Python
one-liner) that the hook never sees. Whether it does depends on the model
and your approvals. **Deny that shell request if you're asked.** This is
the key lesson. Enforcement covers exactly what it matches. Lab 6 closes
this gap with permission rules.

## 4. The PostToolUse hook catches a regression

```text
Refactor pricing.py to compute with floats and round at the end; it reads better.
```

**Observe:** the rule says no floats, so Claude may push back (the rule
working as an *instruction*). If it does refactor, run the suite yourself.
Any failure the PostToolUse hook reports after the edit goes straight back
into the loop, and you'll see Claude react to it without being asked.

## Record

- Which prompts the rule influenced, and whether it complied.
- Every hook block or hook failure message, and what Claude did next.
- Any workaround attempt in step 3, and how you'd prevent it.

## Checkpoint

Revert anything you don't want to keep (`git restore .`), make sure tests
pass, commit the member discount if you kept it, then:

```powershell
git tag lab02b-done
```
