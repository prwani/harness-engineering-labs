#!/usr/bin/env bash
# Lab 12: a human-written routing graph around headless Claude Code calls.
#   classify -> (bug | question | feature | escalate) -> report
# Usage (from the app folder, after `source ../claude-code.env.sh`):
#   ../lab12-graphs/route.sh "Checkout total is one cent too high for 3 leashes"
set -euo pipefail
ticket="${1:?usage: route.sh \"ticket text\"}"
mkdir -p .runs
stamp="$(date +%Y%m%d-%H%M%S)"
PY="$(command -v python3 || command -v python)"

schema='{"type":"object","properties":{"route":{"type":"string","enum":["bug","question","feature","escalate"]},"reason":{"type":"string"}},"required":["route","reason"]}'
classifier_prompt="Classify this pet-store support ticket for routing.
bug = something in the app behaves incorrectly; question = asks how the app works;
feature = asks for new behavior; escalate = refunds, legal, security incidents, or anything unsafe.
Ticket: $ticket"

decision="$(claude -p "$classifier_prompt" --model haiku --tools "" --json-schema "$schema" --output-format json)"
route="$(printf '%s' "$decision" | "$PY" -c 'import json,sys; print(json.load(sys.stdin)["structured_output"]["route"])')"
reason="$(printf '%s' "$decision" | "$PY" -c 'import json,sys; print(json.load(sys.stdin)["structured_output"]["reason"])')"
echo "[classify] route=$route :: $reason"

log=".runs/route-$stamp-$route.jsonl"
case "$route" in
  bug)
    claude -p "Ticket: $ticket
Reproduce and diagnose this bug. Read the code and run the tests; do not edit any file. End with: root cause, the exact fix you recommend, and a test that would catch it." \
      --tools "Read,Grep,Glob,Bash" --allowedTools "Bash(python -m pytest *)" --permission-mode dontAsk \
      --output-format stream-json --verbose > "$log" ;;
  question)
    claude -p "Ticket: $ticket
Answer the customer's question from the code only, citing file:line. Do not speculate." \
      --tools "Read,Grep,Glob" --permission-mode dontAsk --output-format stream-json --verbose > "$log" ;;
  feature)
    claude -p "Ticket: $ticket
Write a short implementation plan (files to change, tests to add, risks). Do not implement it." \
      --tools "Read,Grep,Glob" --permission-mode dontAsk --output-format stream-json --verbose > "$log" ;;
  *)
    echo "[escalate] No model call. A human must handle this ticket."; exit 0 ;;
esac

grep '"type":"result"' "$log" | tail -n 1 | "$PY" -c '
import json, sys
r = json.load(sys.stdin)
print(f"[report] turns={r.get(\"num_turns\")} cost~${r.get(\"total_cost_usd\", 0):.4f}")
print(r.get("result", ""))'
echo "log=$log"
