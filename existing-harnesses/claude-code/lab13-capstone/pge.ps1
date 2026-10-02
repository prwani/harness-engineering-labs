<#
.SYNOPSIS
  Lab 13: planner -> generator -> evaluator, with at most 2 revision rounds.
  Each role is a separate headless Claude Code session with its own tools.

.EXAMPLE
  # from the app folder on a fresh branch, after dot-sourcing ..\claude-code.env.ps1
  ..\lab13-capstone\pge.ps1 -Feature "Add a 'receipt' CLI command that prints an itemized receipt"
#>
param(
    [Parameter(Mandatory)] [string] $Feature,
    [int] $MaxRevisions = 2
)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force .runs | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'

function Invoke-Node([string] $Name, [string[]] $ClaudeArgs) {
    $log = ".runs/pge-$stamp-$Name.jsonl"
    claude @ClaudeArgs --output-format stream-json --verbose > $log
    $final = Get-Content $log | Where-Object { $_ -like '{*"type":"result"*' } | Select-Object -Last 1 | ConvertFrom-Json
    Write-Host ("[{0}] turns={1} cost~`${2} log={3}" -f $Name, $final.num_turns, [math]::Round($final.total_cost_usd, 4), $log) -ForegroundColor Cyan
    return $final
}

# Planner: read-only; the script, not the model, writes PLAN.md.
$plan = Invoke-Node 'planner' @('-p', @"
Feature request: $Feature
Read the codebase and write an implementation plan in Markdown with sections:
Goal, Files to change, Steps, Acceptance criteria (numbered, each one objectively checkable,
including the exact pytest tests that must exist and pass). Output only the plan.
"@, '--tools', 'Read,Grep,Glob', '--permission-mode', 'dontAsk')
$plan.result | Set-Content -Encoding utf8 PLAN.md
Write-Host "PLAN.md written. Review it now; press Enter to continue or Ctrl+C to stop." -ForegroundColor Yellow
[void](Read-Host)

$schema = '{"type":"object","properties":{"verdict":{"type":"string","enum":["PASS","FAIL"]},"failed_criteria":{"type":"array","items":{"type":"string"}},"feedback":{"type":"string"}},"required":["verdict","failed_criteria","feedback"]}'
$feedback = ''
for ($round = 0; $round -le $MaxRevisions; $round++) {
    # Generator: may edit files and run tests; nothing else.
    $genPrompt = "Implement PLAN.md exactly. Run python -m pytest -q until it passes. Do not commit."
    if ($feedback) { $genPrompt += "`nAn independent evaluator rejected the previous attempt:`n$feedback`nFix only what it reports." }
    [void](Invoke-Node "generator-$round" @('-p', $genPrompt,
        '--tools', 'Read,Grep,Glob,Edit,Write,Bash',
        '--allowedTools', 'Edit', 'Write', 'Bash(python -m pytest *)',
        '--permission-mode', 'dontAsk'))

    # Evaluator: fresh session, read-only plus tests and diff, schema-checked verdict.
    $eval = Invoke-Node "evaluator-$round" @('-p', @"
You are a strict reviewer who did not write this code. Compare the working-tree changes
(git diff, plus any new untracked files listed by git status) against every acceptance
criterion in PLAN.md. Run python -m pytest -q yourself. A criterion passes only with evidence.
"@, '--tools', 'Read,Grep,Glob,Bash',
        '--allowedTools', 'Bash(python -m pytest *)', 'Bash(git diff*)', 'Bash(git status*)',
        '--permission-mode', 'dontAsk', '--json-schema', $schema)
    $verdict = $eval.structured_output
    Write-Host "[evaluator-$round] $($verdict.verdict) $($verdict.failed_criteria -join '; ')" -ForegroundColor Magenta
    if ($verdict.verdict -eq 'PASS') { Write-Host 'Accepted. Review git diff, then commit it yourself.' -ForegroundColor Green; return }
    $feedback = "Failed criteria: $($verdict.failed_criteria -join '; ')`n$($verdict.feedback)"
}
Write-Host "Still FAIL after $MaxRevisions revisions. Stopping; a human decides next." -ForegroundColor Red
