from pathlib import Path
import shutil

from harness.approval import Decision
from harness.permissions import Permissions

ASSETS = Path(__file__).resolve().parents[1] / "assets"


def test_lab_settings_rules(tmp_path):
    shutil.copytree(ASSETS, tmp_path, dirs_exist_ok=True)
    permissions = Permissions.load(tmp_path)

    def decide(tool, **args):
        return permissions.decide(tool, args)[0]

    assert decide("run_tests") is Decision.ALLOW
    assert decide("git_cli", args=["status", "--short"]) is Decision.ALLOW
    assert decide("git_cli", args=["commit", "-m", "x"]) is Decision.ASK
    assert decide("git_cli", args=["push", "origin", "main"]) is Decision.DENY
    assert decide("read_file", path=".env") is Decision.DENY
    assert decide("read_file", path=".env.local") is Decision.DENY
    assert decide("edit_file", path="catalog.csv") is Decision.DENY
    assert decide("write_file", path="PRICES.md") is Decision.ASK
    # The documented gap: a broad allow rule lets another tool read the same file.
    assert decide("git_cli", args=["diff", "--no-index", "/dev/null", ".env"]) is Decision.ALLOW
