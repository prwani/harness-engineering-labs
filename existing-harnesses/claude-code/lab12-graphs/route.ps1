<#
.SYNOPSIS
  Lab 12: a human-written routing graph around headless Claude Code calls.
  classify -> (bug | question | feature | escalate) -> report

.EXAMPLE
  # from the app folder, after dot-sourcing ..\claude-code.env.ps1
  ..\lab12-graphs\route.ps1 -Ticket "Checkout total is one cent too high for 3 leashes"
#>
param(
    [Parameter(Mandatory)] [string] $Ticket
)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force .runs | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'

# Node 1: classifier. Cheap model, no tools, schema-validated output.
$schema = '{"type":"object","properties":{"route":{"type":"string","enum":["bug","question","feature","escalate"]},"reason":{"type":"string"}},"required":["route","reason"]}'
$classifierPrompt = @"
Classify this pet-store support ticket for routing.
bug = something in the app behaves incorrectly; question = asks how the app works;
feature = asks for new behavior; escalate = refunds, legal, security incidents, or anything unsafe.
Ticket: $Ticket
"@
$decision = (claude -p $classifierPrompt --model haiku --tools "" --json-schema $schema --output-format json |
    ConvertFrom-Json).structured_output
Write-Host "[classify] route=$($decision.route) :: $($decision.reason)" -ForegroundColor Cyan

# Node 2: one specialist per route, each with a different tool envelope.
$log = ".runs/route-$stamp-$($decision.route).jsonl"
switch ($decision.route) {
    'bug' {
        claude -p "Ticket: $Ticket`nReproduce and diagnose this bug. Read the code and run the tests; do not edit any file. End with: root cause, the exact fix you recommend, and a test that would catch it." `
            --tools "Read,Grep,Glob,Bash" --allowedTools "Bash(python -m pytest *)" --permission-mode dontAsk `
            --output-format stream-json --verbose > $log
    }
    'question' {
        claude -p "Ticket: $Ticket`nAnswer the customer's question from the code only, citing file:line. Do not speculate." `
            --tools "Read,Grep,Glob" --permission-mode dontAsk --output-format stream-json --verbose > $log
    }
    'feature' {
        claude -p "Ticket: $Ticket`nWrite a short implementation plan (files to change, tests to add, risks). Do not implement it." `
            --tools "Read,Grep,Glob" --permission-mode dontAsk --output-format stream-json --verbose > $log
    }
    default {
        Write-Host "[escalate] No model call. A human must handle this ticket." -ForegroundColor Yellow
        return
    }
}

# Node 3: report.
$final = Get-Content $log | Where-Object { $_ -like '{*"type":"result"*' } | Select-Object -Last 1 | ConvertFrom-Json
Write-Host "[$($decision.route)] turns=$($final.num_turns) cost~`$$([math]::Round($final.total_cost_usd, 4)) log=$log" -ForegroundColor Cyan
$final.result
