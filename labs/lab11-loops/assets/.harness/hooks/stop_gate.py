"""Stop hook: don't let the model finish while the test suite is red.

The harness runs this when the model gives its final answer, with the event
as JSON on stdin. Exit code 2 sends stderr back to the model and the loop
continues. The hook doesn't count attempts: the harness stops asking after
3 blocks per question, and --max-iterations bounds the whole run.
"""
import json
import subprocess
import sys

event = json.load(sys.stdin)
result = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider"],
    cwd=event.get("cwd") or ".",
    capture_output=True,
    text=True,
)
if result.returncode in (0, 5):  # 5: no tests collected
    sys.exit(0)

tail = "\n".join((result.stdout + result.stderr).strip().splitlines()[-20:])
print(
    "stop_gate.py: pytest is failing. Fix the code (not the tests) and run the suite again.\n"
    + tail,
    file=sys.stderr,
)
sys.exit(2)
