# Lab 4 — Plan mode: review the plan before any edit

**Start from:** `app/` at tag `lab03-done`, with the Lab 0 setup loaded
(see [Working in `app/`](../README.md#working-in-app)).

**Goal:** for a feature that touches several files, have the harness
produce a plan **with no write tools available**, change the plan, and
only then let it edit. Afterwards, compare what it planned with what it
actually did.

## 1. Plan without editing

Branch first, so approving the plan is cheap to undo:

```powershell
git switch -c feature/discount-codes
claude --permission-mode plan
```

(In a running session, `Shift+Tab` cycles the mode to **plan mode** too.)

```text
Add discount codes to orders:
- codes live in a new discounts.csv: code,kind,value,expires (kind is percent or cents)
- SAVE10 = 10 percent, FLAT500 = 500 cents off, plus one already-expired code
- `python cli.py total P1:2 --code SAVE10` applies it; expired or unknown codes are rejected with a clear message
- a discount can never make the total negative
Plan this change.
```

**Observe:** Claude reads files and maybe runs read-only commands, but
cannot edit. It ends with a plan and asks how to proceed.

## 2. Steer the plan

Don't approve yet. Reply with feedback such as:

```text
Changes: use a dataclass for discount codes, no new dependencies, apply the discount before tax, and list every test you will add.
```

**Observe:** the plan is revised. Save a copy of the final plan, for
example by copying it into `PLAN-discount-codes.md` yourself, or
`Ctrl+G` to open it in your editor if offered.

## 3. Approve and implement

Approve the plan. Choose the option that auto-accepts edits only if you
are happy with the plan. Let it implement and run the tests.

## 4. Compare plan vs reality

```powershell
git diff --stat main
```

Check against the plan: same files? Every promised test present? Anything
it did that the plan didn't mention?

When you're satisfied, commit (or ask Claude to commit) on the branch and
merge into `main`:

```powershell
git switch main ; git merge --no-ff feature/discount-codes
```

## Record

- Tools used in plan mode vs after approval.
- Differences between the final plan and `git diff --stat`.
- Whether your feedback (dataclass, before-tax) actually landed in code.

## Checkpoint

```powershell
python -m pytest -q
git tag lab04-done
```
