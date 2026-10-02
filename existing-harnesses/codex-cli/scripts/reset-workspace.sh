#!/usr/bin/env bash
set -euo pipefail

if (( $# < 1 || $# > 2 )); then
  echo "Usage: bash reset-workspace.sh <lab-folder> [--second]" >&2
  exit 1
fi
lab="$1"
case "$lab" in
  lab00-setup|lab01-baseline|lab02-tool-loop|lab02b-hooks|lab03-sessions|lab04-planning|lab05-file-memory|lab06-approval|lab07-observability|lab08-skills-tools|lab09-background-agents|lab10-compaction|lab11-loops|lab12-graphs|lab13-capstone|lab14-comparison) ;;
  *) echo "Unknown lab: $lab" >&2; exit 1 ;;
esac
folder=workspace
if (( $# == 2 )); then
  if [[ "$2" != --second ]]; then
    echo "Unknown option: $2" >&2
    exit 1
  fi
  folder=workspace-b
fi
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
lab_path="$root/$lab"
workspace="$lab_path/$folder"
if [[ ! -f "$lab_path/README.md" || -L "$lab_path" || -L "$workspace" ]]; then
  echo "Missing lab or linked workspace; refusing reset." >&2
  exit 1
fi
mkdir -p "$workspace"
if [[ -n "$(find "$workspace" -type l -print -quit)" ]]; then
  echo "Remove workspace links manually before resetting." >&2
  exit 1
fi
printf 'Delete contents of %s (except .gitkeep)? Type yes: ' "$workspace"
read -r answer
if [[ "$answer" != yes ]]; then
  echo "Reset cancelled." >&2
  exit 1
fi
while IFS= read -r -d '' item; do
  rm -rf -- "$item"
done < <(find "$workspace" -mindepth 1 -maxdepth 1 ! -name .gitkeep -print0)
touch "$workspace/.gitkeep"
echo "Reset: $workspace. Codex history in CODEX_HOME was not deleted."
