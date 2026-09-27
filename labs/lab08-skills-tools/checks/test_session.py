from harness.session import Session


def test_session_persists_and_resumes(tmp_path):
    path = tmp_path / "session.jsonl"
    session = Session(session_id="session-1")
    session.append({"role": "user", "content": "hello"}, path)
    session.append({"role": "assistant", "content": "hi"}, path)

    resumed = Session.resume(path)

    assert resumed.session_id == "session-1"
    assert resumed.messages == session.messages
