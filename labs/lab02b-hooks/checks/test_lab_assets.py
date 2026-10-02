"""Lab 2B only: the copyable `.harness/` assets work with the harness hooks."""

import shutil
from pathlib import Path

from harness.hooks import load_project_hooks
from harness.tools import build_tools


def test_lab_assets_protect_catalog_and_feed_back_test_failures(tmp_path):
    shutil.copytree(Path(__file__).resolve().parents[1] / "assets", tmp_path, dirs_exist_ok=True)
    (tmp_path / "catalog.csv").write_text("sku,name,price_cents,stock\nP1,Food,100,3\n")
    (tmp_path / "pricing.py").write_text("def total(cents):\n    return cents\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_pricing.py").write_text(
        "from pricing import total\n\ndef test_total():\n    assert total(100) == 100\n"
    )
    (tmp_path / "conftest.py").write_text("")
    events = []
    pipeline = load_project_hooks(tmp_path, lambda *event: events.append(event))

    denial = pipeline.before_tool("edit_file", {"path": "catalog.csv", "old_text": "100", "new_text": "200"})
    assert not denial.allowed and "protect_catalog.py" in denial.reason

    tools, _ = build_tools(tmp_path)
    args = {"path": "pricing.py", "old_text": "return cents", "new_text": "return cents + 1"}
    output = pipeline.after_tool("edit_file", args, tools["edit_file"](args))

    assert "Project rule pricing.md applies to pricing.py" in output
    assert "run_tests.py: pytest FAILED after editing pricing.py" in output
    assert events[0] == ("edit_file", "loaded rule pricing.md for pricing.py")
    assert events[1][1].startswith("run_tests.py: pytest FAILED")
