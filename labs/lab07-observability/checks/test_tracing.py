import json

from typer.testing import CliRunner

from harness.cli import learner
from harness.cli.app import app
from harness.ledger import Usage
from harness.models import ToolCall, Turn
from harness.tracing import MAX_FIELD_CHARS, scrub, summarize

runner = CliRunner()


class Scripted:
    def __init__(self, *turns):
        self.turns = iter(turns)

    def complete(self, **_):
        return next(self.turns)


def script():
    return Scripted(
        Turn(text="", usage=Usage(1000, 50, cached_tokens=200), tool_calls=[
            ToolCall("w", "write_file", {"path": "stats.py", "content": "API_KEY=abc123\n"}),
            ToolCall("r", "read_file", {"path": "missing.py"}),
        ]),
        Turn(text="Done.", usage=Usage(1500, 100)),
    )


def events(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def test_scrub_redacts_and_truncates():
    assert scrub("FAKE_PAYMENT_KEY=sk_test_FAKE") == "FAKE_PAYMENT_KEY=[REDACTED]"
    assert scrub("Bear" + "er abc.def") == "[REDACTED]"
    assert len(scrub("x" * 2000)) < MAX_FIELD_CHARS + 30


def test_trace_records_every_step(tmp_path, monkeypatch):
    monkeypatch.setattr(learner, "create_model_client", script)
    trace = tmp_path / ".runs" / "run.jsonl"

    result = runner.invoke(app, ["ask", "--repo", str(tmp_path), "--accept-edits",
                                 "--trace", str(trace), "Add stats"])

    assert result.exit_code == 0, result.output
    names = [event["event"] for event in events(trace)]
    assert names[0] == "run_start" and names[-1] == "run_end"
    assert names.count("model_call") == 2 and names.count("tool_call") == 2
    assert names.count("permission") == 2 and names.count("tool_result") == 2
    statuses = [event["status"] for event in events(trace) if event["event"] == "tool_result"]
    assert statuses == ["ok", "error"]
    assert "abc123" not in trace.read_text()
    assert (tmp_path / "stats.py").read_text() == "API_KEY=abc123\n"
    end = events(trace)[-1]
    assert end["llm_calls"] == 2 and end["tool_calls"] == 2 and end["error"] is None


def test_summary_folds_the_events(tmp_path, monkeypatch):
    monkeypatch.setattr(learner, "create_model_client", script)
    trace = tmp_path / "run.jsonl"
    runner.invoke(app, ["ask", "--repo", str(tmp_path), "--accept-edits", "--trace", str(trace), "Add stats"])

    text = summarize(trace)
    assert "llm calls" in text and "input=2500, output=150, cached=200" in text
    assert "write_file=1" in text and "read_file=1" in text
    assert "error=1, ok=1" in text and "allow=2" in text
    assert "n/a" in text

    result = runner.invoke(app, ["trace", str(trace), "--input-price", "3", "--output-price", "15"])
    assert "$0.0097" in result.output


def test_cost_and_context_commands(tmp_path, monkeypatch):
    monkeypatch.setattr(learner, "create_model_client", script)
    monkeypatch.delenv("HARNESS_PRICE_INPUT", raising=False)

    result = runner.invoke(app, ["ask", "--repo", str(tmp_path), "--accept-edits"],
                           input="/context\nAdd stats\n/cost\n/context\n/exit\n")

    assert result.exit_code == 0, result.output
    assert "No model call yet" in result.output
    assert "LLM calls: 2" in result.output and "input=2500, output=150" in result.output
    assert "Last request: 1500 input tokens" in result.output
    assert "tool results" in result.output
