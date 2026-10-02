"""pre_tool hook: refuse direct edits to catalog.csv.

The harness sends the pending tool call as JSON on stdin. Exit code 2
blocks the call and returns stderr to the model as the denial reason;
exit code 0 lets the call run.
"""
import json
import sys

call = json.load(sys.stdin)
path = str((call.get("args") or {}).get("path", ""))

if path.replace("\\", "/").endswith("catalog.csv"):
    print(
        "BLOCKED by protect_catalog.py: catalog.csv is the product source of "
        "truth and must not be edited by the agent. Ask the human to change it.",
        file=sys.stderr,
    )
    sys.exit(2)

sys.exit(0)
