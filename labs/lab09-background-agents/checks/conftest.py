import pytest


@pytest.fixture(autouse=True)
def isolated_harness_home(tmp_path_factory, monkeypatch):
    """Keep sessions and other per-user harness state out of the real home folder."""
    monkeypatch.setenv("HARNESS_HOME", str(tmp_path_factory.mktemp("harness-home")))
