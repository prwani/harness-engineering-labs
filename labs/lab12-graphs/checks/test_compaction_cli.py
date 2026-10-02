import json

from typer.testing import CliRunner

from harness.chat import Chat
from harness.cli import learner
from harness.cli.app import app
from harness.compaction import SUMMARY_HEADER
from harness.ledger import Usage
from harness.models import Turn
from harness.session import SessionStore
from harness.tools import build_tools

runner = CliRunner()


class Recorder:
    def __init__(self, *turns):
        self.turns = iter(turns)
        self.calls = []

    def complete(self, *, system, messages, tools, **_):
        self.calls.append({"system": system, "messages": list(messages), "tools": tools})
        return next(self.turns)


def test_read_file_reads_large_files_in_line_ranges(tmp_path):
    (tmp_path / "app.log").write_text("".join(f"line {n} " + "x" * 80 + "\n" for n in range(1, 3001)))
    tools, definitions = build_tools(tmp_path)
    schema = next(item for item in definitions if item["name"] == "read_file")["input_schema"]
    assert {"start_line", "max_lines"} <= set(schema["properties"])

    try:
        tools["read_file"]({"path": "app.log"})
    except ValueError as error:
        assert "start_line and max_lines" in str(error)
    else:
        raise AssertionError("whole-file read of a large file should fail")
    part = tools["read_file"]({"path": "app.log", "start_line": 1000, "max_lines": 5000})
    assert part.startswith("[lines 1000-1999 of 3000]\nline 1000 ")
    assert tools["read_file"]({"path": "app.log", "start_line": 2999}).count("\n") == 2

    (tmp_path / "medium.txt").write_text("y" * 30_000)
    assert "[truncated at 20,000 of 30,000 characters" in tools["read_file"]({"path": "medium.txt"})


def test_reset_entries_restart_a_resumed_session(tmp_path, monkeypatch):
    monkeypatch.setenv("HARNESS_HOME", str(tmp_path / "home"))
    store = SessionStore(tmp_path)
    session = store.create("investigate")
    session.append({"role": "user", "content": "first question"}, session.path)
    session.append({"role": "assistant", "content": "long answer"}, session.path)
    session.replace([{"role": "user", "content": "summary"}])

    resumed = store.load(store.find("investigate"))
    assert resumed.messages == [{"role": "user", "content": "summary"}]
    assert store.list()[0].title == "first question"
    assert "long answer" in session.path.read_text()


def test_compact_replaces_history_with_a_guided_summary(tmp_path, monkeypatch):
    monkeypatch.setenv("HARNESS_HOME", str(tmp_path / "home"))
    model = Recorder(Turn(text="Root cause: timeout 5000 -> 500."), Turn(text="Deploy 7f3a2c."),
                     Turn(text="It was 7f3a2c."))
    monkeypatch.setattr(learner, "create_model_client", lambda: model)
    repo = ["--repo", str(tmp_path)]

    assert runner.invoke(app, ["ask", *repo, "-n", "inc", "Investigate app.log"]).exit_code == 0
    result = runner.invoke(app, ["ask", *repo, "-c", "/compact Keep the deploy id."])

    assert result.exit_code == 0, result.output
    assert "Compacted ~" in result.output and "Deploy 7f3a2c." in result.output
    request = model.calls[1]
    assert "Keep the deploy id." in request["messages"][-1]["content"]
    assert request["messages"][0]["content"] == "Investigate app.log"
    assert {tool["name"] for tool in request["tools"]} >= {"read_file"}

    assert runner.invoke(app, ["ask", *repo, "-c", "Which deploy?"]).exit_code == 0
    sent = model.calls[2]["messages"]
    assert sent[0]["content"].startswith(SUMMARY_HEADER) and "Deploy 7f3a2c." in sent[0]["content"]
    assert len(sent) == 3 and "Investigate app.log" not in json.dumps(sent)


def test_clear_and_auto_compaction(tmp_path, monkeypatch):
    monkeypatch.setenv("HARNESS_HOME", str(tmp_path / "home"))
    model = Recorder(Turn(text="answer", usage=Usage(input_tokens=5000)), Turn(text="summary"))
    chat = Chat(model, tmp_path, SessionStore(tmp_path).create(), compact_at=4000)
    assert not chat.needs_compaction()
    chat.ask("question")
    assert chat.needs_compaction()
    before, after, summary = chat.compact()
    assert summary == "summary" and after > 0 and len(chat.session.messages) == 2
    chat.clear()
    assert chat.session.messages == [] and not chat.needs_compaction()


def test_compact_at_compacts_before_the_next_question(tmp_path, monkeypatch):
    monkeypatch.setenv("HARNESS_HOME", str(tmp_path / "home"))
    model = Recorder(Turn(text="big", usage=Usage(input_tokens=9000)), Turn(text="the summary"),
                     Turn(text="small"))
    monkeypatch.setattr(learner, "create_model_client", lambda: model)
    answers = iter(["first", "second", "/exit"])
    monkeypatch.setattr("builtins.input", lambda _="": next(answers))

    result = runner.invoke(app, ["ask", "--repo", str(tmp_path), "--compact-at", "8000"])

    assert result.exit_code == 0, result.output
    assert "(--compact-at 8000); compacting first." in result.output
    assert model.calls[2]["messages"][0]["content"].endswith("the summary")
