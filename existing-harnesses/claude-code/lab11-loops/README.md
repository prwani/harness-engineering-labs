# Lab 11 — Loops with a stop condition

**Start from:** `app/` at tag `lab10-done`, with the Lab 0 setup loaded
(see [Working in `app/`](../README.md#working-in-app)).

**Goal:** make "done" something the harness checks, not something the
model claims. You add a failing test (the spec), then compare three
loops:

1. **Prompted loop**: the model is asked to keep going until tests pass.
2. **Stop hook**: [`stop_gate.py`](assets/.claude/hooks/stop_gate.py)
   runs pytest whenever Claude tries to finish and sends it back to work
   while tests fail. It gives up after 3 blocks, so it can't loop
   forever.
3. **Script loop**: an outer loop you own, bounded and checked by plain
   code.

The spec, [`tests/test_bulk_discount.py`](assets/tests/test_bulk_discount.py):
`pricing.bulk_discount_percent(qty)` returns 0 below 10, 5 for 10–49, 10
for 50 or more, and raises `ValueError` for qty ≤ 0. The new settings deny
edits to that test file, so the model can't "pass" by changing the spec.

## 1. Add the spec (red)

```powershell
git switch -c feature/bulk-discount
Copy-Item -Force ..\lab11-loops\assets\tests\test_bulk_discount.py tests\
python -m pytest -q          # should fail
git add tests ; git commit -m "test: bulk discount spec"
```

```sh
git switch -c feature/bulk-discount
cp ../lab11-loops/assets/tests/test_bulk_discount.py tests/
python -m pytest -q
git add tests && git commit -m "test: bulk discount spec"
```

## 2. Prompted loop (no gate)

```powershell
claude -p "Implement pricing.bulk_discount_percent so tests/test_bulk_discount.py passes. Keep running the tests and fixing until they all pass." --permission-mode acceptEdits --max-budget-usd 1
python -m pytest -q
git stash -u      # set the attempt aside to compare later
```

It usually works for a task this small. The question is *who* verified
it: only the model.

## 3. Stop hook gate

```powershell
Copy-Item -Recurse -Force ..\lab11-loops\assets\.claude .
claude -p "Implement pricing.bulk_discount_percent. Be brief." --permission-mode acceptEdits --max-budget-usd 1 `
  --output-format stream-json --verbose --include-hook-events > .runs\lab11-stop.jsonl
python ..\lab07-observability\analyze_stream.py .runs\lab11-stop.jsonl
```

```sh
cp -R ../lab11-loops/assets/.claude .
claude -p "Implement pricing.bulk_discount_percent. Be brief." --permission-mode acceptEdits --max-budget-usd 1 \
  --output-format stream-json --verbose --include-hook-events > .runs/lab11-stop.jsonl
python ../lab07-observability/analyze_stream.py .runs/lab11-stop.jsonl
```

The prompt doesn't even mention tests. **Observe** in the hook events:
if Claude stops early, the Stop hook blocks it with the failing test
output and the loop continues. `--max-budget-usd` is a second, cost-based
bound.

## 4. Script loop (you own the loop)

```powershell
git restore pricing.py     # start from red again; keep the Lab 11 settings
for ($i = 1; $i -le 3; $i++) {
    python -m pytest -q tests/test_bulk_discount.py
    if ($LASTEXITCODE -eq 0) { Write-Host "green after $($i-1) attempt(s)"; break }
    claude -p "Tests in tests/test_bulk_discount.py fail. Make one focused change to pricing.py to fix them." --permission-mode acceptEdits --max-budget-usd 0.5
}
```

```sh
git restore pricing.py
for i in 1 2 3; do
  python -m pytest -q tests/test_bulk_discount.py && { echo "green after $((i-1)) attempt(s)"; break; }
  claude -p "Tests in tests/test_bulk_discount.py fail. Make one focused change to pricing.py to fix them." --permission-mode acceptEdits --max-budget-usd 0.5
done
```

Here the stop condition, bound and verification are ordinary code; each
iteration is a fresh session with no memory of the last one.

## Record

| Loop | Who checks "done"? | Bound | Iterations / turns | Cost |
|---|---|---|---|---|

## Checkpoint

Keep the best implementation (drop the stash with `git stash drop`),
commit, merge:

```powershell
python -m pytest -q
git add .claude pricing.py ; git commit -m "feat: bulk discount with stop-hook gate"
git switch main ; git merge --no-ff feature/bulk-discount
git tag lab11-done
```
