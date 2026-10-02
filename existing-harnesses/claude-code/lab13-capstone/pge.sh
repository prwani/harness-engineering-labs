#!/usr/bin/env bash
# Lab 13: planner -> generator -> evaluator, with at most 2 revision rounds.
# Usage (from the app folder on a fresh branch, after `source ../claude-code.env.sh`):
#   ../lab13-capstone/pge.sh "Add a 'receipt' CLI command that prints an itemized receipt"
set -euo pipefail
feature="${1:?usage: pge.sh \"feature request\"}"
max_revisions="${2:-2}"
mkdir -p .runs
stamp="$(date +%Y%m%d-%H%M%S)"
PY="$(command -v python3 || command -v python)"

# run_node NAME claude-args... ; prints the final result JSON line on stdout
run_node() {
  local name="$1"; shift
  local log=".runs/pge-$stamp-$name.jsonl"
  claude "$@" --output-format stream-json --verbose > "$log"
  local final; final="$(grep '"type":"result"' "$log" | tail -n 1)"
  printf '%s' "$final" | "$PY" -c "import json,sys; r=json.load(sys.stdin); print(f'[$name] turns={r.get(\"num_turns\")} cost~\${r.get(\"total_cost_usd\",0):.4f} log=$log')" >&2
  printf '%s' "$final"
}
field() { "$PY" -c "import json,sys; r=json.load(sys.stdin); v=r$1; print(v if isinstance(v,str) else json.dumps(v))"; }

plan_json="$(run_node planner -p "Feature request: $feature
Read the codebase and write an implementation plan in Markdown with sections:
Goal, Files to change, Steps, Acceptance criteria (numbered, each one objectively checkable,
including the exact pytest tests that must exist and pass). Output only the plan." \
  --tools "Read,Grep,Glob" --permission-mode dontAsk)"
printf '%s' "$plan_json" | field '["result"]' > PLAN.md
read -r -p "PLAN.md written. Review it now; press Enter to continue or Ctrl+C to stop. " _

schema='{"type":"object","properties":{"verdict":{"type":"string","enum":["PASS","FAIL"]},"failed_criteria":{"type":"array","items":{"type":"string"}},"feedback":{"type":"string"}},"required":["verdict","failed_criteria","feedback"]}'
feedback=""
for ((round = 0; round <= max_revisions; round++)); do
  gen_prompt="Implement PLAN.md exactly. Run python -m pytest -q until it passes. Do not commit."
  [[ -n "$feedback" ]] && gen_prompt="$gen_prompt
An independent evaluator rejected the previous attempt:
$feedback
Fix only what it reports."
  run_node "generator-$round" -p "$gen_prompt" \
    --tools "Read,Grep,Glob,Edit,Write,Bash" \
    --allowedTools "Edit" "Write" "Bash(python -m pytest *)" \
    --permission-mode dontAsk > /dev/null

  eval_json="$(run_node "evaluator-$round" -p "You are a strict reviewer who did not write this code. Compare the working-tree changes
(git diff, plus any new untracked files listed by git status) against every acceptance
criterion in PLAN.md. Run python -m pytest -q yourself. A criterion passes only with evidence." \
    --tools "Read,Grep,Glob,Bash" \
    --allowedTools "Bash(python -m pytest *)" "Bash(git diff*)" "Bash(git status*)" \
    --permission-mode dontAsk --json-schema "$schema")"
  verdict="$(printf '%s' "$eval_json" | field '["structured_output"]["verdict"]')"
  failed="$(printf '%s' "$eval_json" | field '["structured_output"]["failed_criteria"]')"
  echo "[evaluator-$round] $verdict $failed"
  if [[ "$verdict" == "PASS" ]]; then echo "Accepted. Review git diff, then commit it yourself."; exit 0; fi
  feedback="Failed criteria: $failed
$(printf '%s' "$eval_json" | field '["structured_output"]["feedback"]')"
done
echo "Still FAIL after $max_revisions revisions. Stopping; a human decides next."
