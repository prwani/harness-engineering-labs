import json

import pytest

from harness.hooks import load_project_hooks


@pytest.fixture
def lab_app(tmp_path):
    from pathlib import Path
    import shutil

    assets = Path(__file__).resolve().parents[1] / "assets"
    shutil.copytree(assets, tmp_path, dirs_exist_ok=True)
    (tmp_path / "pricing.py").write_text("def bulk_discount_percent(qty):\n    return 0\n")
    return tmp_path


def test_lab11_stop_gate_runs_the_suite(lab_app):
    settings = json.loads((lab_app / ".harness" / "settings.json").read_text())
    stop_only = {"hooks": {"stop": settings["hooks"]["stop"]}}
    (lab_app / ".harness" / "settings.json").write_text(json.dumps(stop_only))

    feedback = load_project_hooks(lab_app).on_stop("done", False)
    assert feedback and "stop_gate.py: pytest is failing" in feedback

    (lab_app / "pricing.py").write_text(
        "def bulk_discount_percent(qty):\n"
        "    if qty <= 0:\n        raise ValueError(qty)\n"
        "    return 10 if qty >= 50 else 5 if qty >= 10 else 0\n")
    assert load_project_hooks(lab_app).on_stop("done", False) is None


def test_lab11_settings_protect_the_spec(lab_app):
    from harness.approval import Decision
    from harness.permissions import Permissions

    permissions = Permissions.load(lab_app, accept_edits=True)
    for tool in ("write_file", "edit_file"):
        decision, _ = permissions.decide(tool, {"path": "tests/test_bulk_discount.py"})
        assert decision is Decision.DENY
    assert permissions.decide("edit_file", {"path": "pricing.py"})[0] is Decision.ALLOW
