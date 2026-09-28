from pathlib import Path

from harness.compaction import CompactionPolicy, build_repo_map, compact, estimate_tokens


def test_compaction_does_not_trigger_below_threshold():
    policy = CompactionPolicy(token_threshold=1000, keep_recent=2)
    messages = [{"role": "user", "content": "short"}]

    result, handoff = compact(policy, messages)

    assert result == messages
    assert handoff is None


def test_compaction_keeps_recent_messages_verbatim():
    policy = CompactionPolicy(token_threshold=10, keep_recent=2)
    messages = [
        {"role": "user", "content": "x" * 100},
        {"role": "assistant", "content": "y" * 100},
        {"role": "user", "content": "recent-1"},
        {"role": "assistant", "content": "recent-2"},
    ]

    result, handoff = compact(policy, messages)

    assert result[-2:] == messages[-2:]
    assert result[0]["role"] == "system"
    assert "[compacted]" in result[0]["content"]
    assert handoff.dropped_message_count == 2


def test_estimate_tokens_grows_with_content_length():
    small = [{"role": "user", "content": "a"}]
    large = [{"role": "user", "content": "a" * 400}]

    assert estimate_tokens(large) > estimate_tokens(small)


def test_repo_map_lists_files_and_dirs(tmp_path):
    (tmp_path / "sandbox").mkdir()
    (tmp_path / "sandbox" / "readme.md").write_text("hi")

    entries = build_repo_map(tmp_path)

    kinds = {entry.path: entry.kind for entry in entries}
    assert kinds[Path("sandbox").as_posix()] == "dir"
    assert kinds[Path("sandbox/readme.md").as_posix()] == "file"
