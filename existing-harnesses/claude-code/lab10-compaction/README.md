# Lab 10 — Context and compaction

**Start from:** `app/` at tag `lab09-done`, with the Lab 0 setup loaded
(see [Working in `app/`](../README.md#working-in-app)).

**Goal:** fill the context with a long investigation, compact it, and
check which facts survive. [`make_log.py`](make_log.py) writes a
6,000-line synthetic `app.log` with a few important facts buried in
noise.

## 1. Generate the incident log

```powershell
python ..\lab10-compaction\make_log.py
```

`app.log` is ignored by the app's `*.log` rule. Don't open it yet.

## 2. Investigate

```powershell
claude
```

```text
Last night checkout failures spiked. Investigate app.log: find the root cause, the deploy involved, the affected order IDs and region, and when it was fixed. Read the whole log and show your evidence.
```

Then:

```text
/context
```

**Observe:** how much of the window the log and tool results take.

## 3. Compact with instructions

```text
/compact Keep: root cause, config key and values, deploy id, affected order IDs and region, rollback time, and the fix plan. Drop raw log lines.
```

Then ask, without letting it re-read the log:

```text
Without reading any files, answer: what config changed, from what to what, in which deploy, which orders failed, in which region, and when was it rolled back?
```

**Check against the answer key:** `payment.timeout_ms` changed from
`5000` to `500` in deploy `7f3a2c`; orders `ORD-2047`, `ORD-2113`,
`ORD-2190` timed out in `eu-west`; then a rollback followed. The
"out of stock sku=P3" lines are noise, not the cause.

## 4. Compare with an unguided compact

Start a new session, repeat step 2, then use plain `/compact` (no
instructions) and ask the same question. Optionally try `/clear` to see
what losing everything looks like.

## Record

| | Facts kept (of 6) | `/context` before | after |
|---|---|---|---|
| `/compact` with instructions | | | |
| plain `/compact` | | | |

Note any hallucinated "facts" after compaction.

## Checkpoint

Nothing to commit (the log is ignored):

```powershell
git tag lab10-done
```
