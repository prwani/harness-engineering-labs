"""PostToolUse hook: run pytest after every Python file edit.

On failure, exit code 2 feeds the test output back to Claude so it sees
the regression immediately, whether or not it planned to run tests.
"""
import json
import os
import subprocess
import sys

call = json.load(sys.stdin)
path = (call.get("tool_input") or {}).get("file_path", "")
if not path.endswith(".py"):
    sys.exit(0)

project = os.environ.get("CLAUDE_PROJECT_DIR") or call.get("cwd") or "."
result = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider"],
    cwd=project,
    capture_output=True,
    text=True,
)
if result.returncode not in (0, 5):  # 5 = no tests collected
    tail = "\n".join((result.stdout + result.stderr).strip().splitlines()[-25:])
    print(f"run_tests.py: pytest FAILED after editing {path}:\n{tail}", file=sys.stderr)
    sys.exit(2)

sys.exit(0)
