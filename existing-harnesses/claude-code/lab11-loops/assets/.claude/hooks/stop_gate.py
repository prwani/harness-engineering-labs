"""Stop hook: do not let Claude finish while the test suite is red.

Exit code 2 blocks the stop and shows stderr to Claude, so it keeps
working. `stop_hook_active` is true when Claude is already continuing
because of this hook; the attempt counter bounds the loop so a stubborn
failure cannot spin forever.
"""
import json
import os
import subprocess
import sys
import tempfile

MAX_BLOCKS = 3

event = json.load(sys.stdin)
project = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or "."
counter = os.path.join(tempfile.gettempdir(), f"stop_gate_{event.get('session_id', 'x')}.count")

result = subprocess.run(
    [sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider"],
    cwd=project,
    capture_output=True,
    text=True,
)
if result.returncode in (0, 5):
    if os.path.exists(counter):
        os.remove(counter)
    sys.exit(0)

blocks = int(open(counter).read()) if os.path.exists(counter) else 0
if blocks >= MAX_BLOCKS:
    print(f"stop_gate.py: tests still failing after {MAX_BLOCKS} forced retries; handing back to the human.", file=sys.stderr)
    os.remove(counter)
    sys.exit(0)

with open(counter, "w") as fh:
    fh.write(str(blocks + 1))
tail = "\n".join((result.stdout + result.stderr).strip().splitlines()[-20:])
print(
    f"stop_gate.py (attempt {blocks + 1}/{MAX_BLOCKS}): you are not done, pytest is failing. "
    f"Fix the code (not the tests) and run the suite again.\n{tail}",
    file=sys.stderr,
)
sys.exit(2)
