import pytest

from harness.memory import (
    CachedArtifact,
    ConcurrencyError,
    FileScope,
    ScopeError,
    SessionMemory,
    SharedStore,
    snapshot_key,
)


def test_session_memory_writes_and_reads(tmp_path):
    memory = SessionMemory(root=tmp_path / "memory")

    memory.write("notes.md", "hello")

    assert memory.read("notes.md") == "hello"


def test_shared_store_write_fails_when_read_only(tmp_path):
    store = SharedStore(root=tmp_path, mode="ro")
    (tmp_path / "catalog.json").write_text("{}")
    _content, version = store.read("catalog.json")

    with pytest.raises(PermissionError):
        store.write("catalog.json", "{}", if_match=version)


def test_two_writers_produce_one_success_and_one_conflict(tmp_path):
    (tmp_path / "catalog.json").write_text("v1")
    store_a = SharedStore(root=tmp_path, mode="rw")
    store_b = SharedStore(root=tmp_path, mode="rw")
    _content_a, version_a = store_a.read("catalog.json")
    _content_b, version_b = store_b.read("catalog.json")

    store_a.write("catalog.json", "v2-from-a", if_match=version_a)

    with pytest.raises(ConcurrencyError):
        store_b.write("catalog.json", "v2-from-b", if_match=version_b)


def test_file_scope_rejects_paths_outside_granted_roots(tmp_path):
    allowed = tmp_path / "sandbox"
    allowed.mkdir()
    scope = FileScope(allowed_roots=(allowed,))

    scope.check(allowed / "notes.md")

    with pytest.raises(ScopeError):
        scope.check(tmp_path / "outside.md")


def test_stale_snapshot_is_reported(tmp_path):
    key_before = snapshot_key(repo_sha="abc", sim_state_version="1", task="m1")
    artifact = CachedArtifact(key=key_before, content="{}")

    key_after_price_change = snapshot_key(repo_sha="abc", sim_state_version="2", task="m1")

    assert not artifact.is_stale(key_before)
    assert artifact.is_stale(key_after_price_change)
