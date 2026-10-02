"""PreToolUse hook: refuse direct edits to catalog.csv.

Claude Code sends the pending tool call as JSON on stdin. Exit code 2
blocks the call and shows stderr to Claude; exit code 0 lets the normal
permission flow continue.
"""
import json
import sys

call = json.load(sys.stdin)
path = (call.get("tool_input") or {}).get("file_path", "")

if path.replace("\\", "/").endswith("catalog.csv"):
    print(
        "BLOCKED by protect_catalog.py: catalog.csv is the product source of "
        "truth and must not be edited by the agent. Ask the human to change it.",
        file=sys.stderr,
    )
    sys.exit(2)

sys.exit(0)
