from pathlib import Path

from harness.lab_features import load_features


def test_snapshot_declares_its_scope(monkeypatch):
    root = Path(__file__).parents[1]
    monkeypatch.chdir(root)

    features = load_features()

    assert features.number == 8
    assert features.slug == 'skills-tools'
    assert features.capabilities
    assert features.live_validation
