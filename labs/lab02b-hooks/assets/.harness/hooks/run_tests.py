"""post_tool hook: run pytest after every Python file edit.

On failure, exit code 2 sends the test output back to the model with the
tool result, so it sees the regression whether or not it planned to test.
On success, the single stdout line is shown to you, not the model.
"""
import json
import subprocess
import sys

call = json.load(sys.stdin)
path = str((call.get("args") or {}).get("path", ""))
if not path.endswith(".py"):
    sys.exit(0)

result = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider"],
    cwd=call.get("cwd") or ".",
    capture_output=True,
    text=True,
)
if result.returncode not in (0, 5):  # 5 = no tests collected
    tail = "\n".join((result.stdout + result.stderr).strip().splitlines()[-25:])
    print(f"run_tests.py: pytest FAILED after editing {path}:\n{tail}", file=sys.stderr)
    sys.exit(2)

print(f"run_tests.py: tests pass after editing {path}")
sys.exit(0)
