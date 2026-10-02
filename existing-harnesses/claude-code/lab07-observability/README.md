# Lab 7 — Observability: see every step, token and cost

**Start from:** `app/` at tag `lab06-done`, with the Lab 0 setup loaded
(see [Working in `app/`](../README.md#working-in-app)).

**Goal:** turn a run into data. You capture one headless run as an event
stream, summarize it with
[`analyze_stream.py`](analyze_stream.py), and compare that with the
interactive views and the saved transcript.

## 1. Capture a headless run

```powershell
New-Item -ItemType Directory -Force .runs | Out-Null
claude -p "Add a 'stats' CLI command that prints product count, total stock units and total inventory value in dollars. Add a test and run the tests. Do not commit." `
  --permission-mode acceptEdits --output-format stream-json --verbose --include-hook-events `
  > .runs\lab07.jsonl
```

```sh
mkdir -p .runs
claude -p "Add a 'stats' CLI command that prints product count, total stock units and total inventory value in dollars. Add a test and run the tests. Do not commit." \
  --permission-mode acceptEdits --output-format stream-json --verbose --include-hook-events \
  > .runs/lab07.jsonl
```

`.runs/` is gitignored. `acceptEdits` auto-approves file edits; your
Lab 6 allow rule covers pytest.

## 2. Summarize it

```powershell
python ..\lab07-observability\analyze_stream.py .runs\lab07.jsonl
```

**Observe:** tool calls by name, hook events (your Lab 2B hooks!), number
of turns, duration, input/output/cache tokens, the reported cost and any
permission denials. Then open the JSONL and find one `tool_use` and its
matching `tool_result`. The summary is just a fold over these events.

> The cost is Claude Code's **list-price estimate**, not your Azure bill.
> Use Azure Cost Management for actual Foundry spend.

## 3. Interactive views

Start `claude -c` (continue the run you just captured; headless runs are
sessions too), then try:

```text
/cost
```

```text
/context
```

```text
/status
```

Press `Ctrl+O` to toggle the detailed transcript view showing tool inputs,
outputs and hook messages.

## 4. Transcripts on disk

Every session is a JSONL file under `~/.claude/projects/<encoded path>/`:

```powershell
Get-ChildItem "$HOME\.claude\projects" -Recurse -Filter *.jsonl |
  Sort-Object LastWriteTime -Descending | Select-Object -First 3 FullName, Length
```

Treat these as sensitive: they contain your prompts, file contents and
command output.

## 5. (Optional) OpenTelemetry

Claude Code can export metrics and events with OpenTelemetry. To see them
on the console:

```powershell
$env:CLAUDE_CODE_ENABLE_TELEMETRY = "1"
$env:OTEL_METRICS_EXPORTER = "console"
$env:OTEL_LOGS_EXPORTER = "console"
claude -p "How many products are in catalog.csv?"
```

In production, point `OTEL_EXPORTER_OTLP_ENDPOINT` at a collector (for
example Azure Monitor) instead. Remove the variables afterwards.

## Record

Turns, tool calls by type, hook events, tokens, estimated cost and
duration for the step 1 run. Keep this table; Lab 14 compares against it.

## Checkpoint

Review and commit the `stats` command if tests pass (or `git restore .`):

```powershell
git tag lab07-done
```
