import json

import pytest
from typer.testing import CliRunner

from harness.cli import learner
from harness.cli.app import app
from harness.hooks import validate_history
from harness.models import ScriptedModel, ToolCall, Turn
from harness.session import SessionStore, to_jsonable
from harness.tool_loop import run_tool_loop

runner = CliRunner()


class RecordingModel:
    """Answers with a fixed text and records the messages of every call."""

    def __init__(self, answers):
        self.answers = iter(answers)
        self.calls = []

    def complete(self, *, messages, **_):
        self.calls.append(json.loads(json.dumps(messages)))
        return Turn(text=next(self.answers))


def test_tool_loop_appends_each_question_and_answer_to_history():
    history, saved = [], []
    model = ScriptedModel([
        Turn(text="", tool_calls=[ToolCall("c1", "echo", {"text": "hi"})]),
        Turn(text="first answer"),
        Turn(text="second answer"),
    ])

    run_tool_loop(model, "q1", "system", {"echo": lambda a: a["text"]},
                  history=history, on_message=saved.append)
    run_tool_loop(model, "q2", "system", {}, history=history, on_message=saved.append)

    assert [m["role"] for m in history] == ["user", "assistant", "tool", "assistant", "user", "assistant"]
    assert history[-1]["content"] == "second answer"
    assert saved == history
    validate_history(history)


def test_validate_history_rejects_tool_result_without_call():
    with pytest.raises(ValueError, match="alternate"):
        validate_history([
            {"role": "user", "content": "q1"},
            {"role": "assistant", "content": "a1"},
            {"role": "tool", "content": [{"call_id": "x", "output": "?"}]},
        ])


def test_continue_sends_the_earlier_conversation(tmp_path, monkeypatch):
    model = RecordingModel(["Plan written.", "P4 is low."])
    monkeypatch.setattr(learner, "create_model_client", lambda: model)

    first = runner.invoke(app, ["ask", "--repo", str(tmp_path), "-n", "low-stock", "Plan it."])
    second = runner.invoke(app, ["ask", "--repo", str(tmp_path), "-c", "Which products are low?"])

    assert first.exit_code == 0, first.output
    assert second.exit_code == 0, second.output
    assert "'low-stock': 2 messages" in second.output
    assert [m["content"] for m in model.calls[1]] == ["Plan it.", "Plan written.", "Which products are low?"]
    listing = runner.invoke(app, ["sessions", "--repo", str(tmp_path)])
    assert "low-stock" in listing.output and "4 msgs" in listing.output


def test_resume_by_name_and_fork_keeps_the_original(tmp_path, monkeypatch):
    model = RecordingModel(["one", "two"])
    monkeypatch.setattr(learner, "create_model_client", lambda: model)
    runner.invoke(app, ["ask", "--repo", str(tmp_path), "-n", "design", "Design A?"])

    result = runner.invoke(app, ["ask", "--repo", str(tmp_path), "-r", "design", "--fork", "Design B?"])

    assert result.exit_code == 0, result.output
    assert "fork of" in result.output
    store = SessionStore(tmp_path)
    sessions = store.list()
    assert len(sessions) == 2
    original = next(info for info in sessions if not info.forked_from)
    fork = next(info for info in sessions if info.forked_from)
    assert fork.forked_from == original.session_id
    assert original.messages == 2 and fork.messages == 4


def test_fork_without_a_session_and_unknown_resume_fail_clearly(tmp_path, monkeypatch):
    monkeypatch.setattr(learner, "create_model_client", lambda: RecordingModel([]))

    forked = runner.invoke(app, ["ask", "--repo", str(tmp_path), "--fork", "x"])
    missing = runner.invoke(app, ["ask", "--repo", str(tmp_path), "-r", "nope", "x"])

    assert forked.exit_code == 1 and "--fork needs" in forked.output
    assert missing.exit_code == 1 and "no session matches" in missing.output


def test_interrupted_tool_call_is_paired_on_resume(tmp_path):
    store = SessionStore(tmp_path)
    session = store.create("crash")
    session.append({"role": "user", "content": "q"}, session.path)
    session.append({"role": "assistant", "content": "", "call_ids": ["c1"]}, session.path)

    resumed = store.load(store.find("crash"))

    assert resumed.messages[-1]["content"][0]["call_id"] == "c1"
    assert "interrupted" in resumed.messages[-1]["content"][0]["output"]
    validate_history(resumed.messages)
    assert store.find("crash").messages == 3  # the repair was saved


def test_interactive_session_and_history_commands(tmp_path, monkeypatch):
    monkeypatch.setattr(learner, "create_model_client", lambda: RecordingModel(["ok"]))

    result = runner.invoke(app, ["ask", "--repo", str(tmp_path)],
                           input="First question\n/history\n/session\n/nope\n/exit\n")

    assert result.exit_code == 0, result.output
    assert "1. First question" in result.output
    assert "File:" in result.output
    assert "Unknown command /nope" in result.output


def test_provider_objects_are_saved_as_plain_json():
    class Block:
        def model_dump(self, **_):
            return {"type": "text", "text": "hi"}

    assert to_jsonable({"content": [Block()]}) == {"content": [{"type": "text", "text": "hi"}]}


def test_responses_adapter_replays_a_saved_text_answer():
    from types import SimpleNamespace

    from harness.models import ResponsesAdapter

    captured = {}

    def create(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace(output=[], usage=None, status="completed")

    client = SimpleNamespace(responses=SimpleNamespace(create=create))
    ResponsesAdapter(client, "gpt").complete(
        system="s", tools=[],
        messages=[{"role": "user", "content": "q1"}, {"role": "assistant", "content": "a1"},
                  {"role": "user", "content": "q2"}],
    )

    assert captured["input"][1] == {"role": "assistant", "content": "a1"}
