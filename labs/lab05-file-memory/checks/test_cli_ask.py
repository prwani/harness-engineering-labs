from typer.testing import CliRunner

from harness.cli import learner
from harness.cli.app import app
from harness.ledger import Usage
from harness.models import Turn


class FakeModel:
    def __init__(self):
        self.questions = []

    def complete(self, *, messages, **kwargs):
        question = messages[-1]["content"]
        self.questions.append(question)
        return Turn(question, usage=Usage(input_tokens=2, output_tokens=1))


def test_interactive_ask_accepts_multiple_independent_questions(monkeypatch):
    model = FakeModel()
    monkeypatch.setattr(learner, "create_model_client", lambda: model)

    result = CliRunner().invoke(
        app, ["ask"], input="What is 1 + 1?\nWhat is the capital of France?\n/exit\n"
    )

    assert result.exit_code == 0
    assert model.questions == ["What is 1 + 1?", "What is the capital of France?"]
    assert result.output.count("Assistant>") == 2
    assert "Tokens: input=2, output=1" in result.output


def test_ask_keeps_one_shot_question_invocation(monkeypatch):
    model = FakeModel()
    monkeypatch.setattr(learner, "create_model_client", lambda: model)

    result = CliRunner().invoke(app, ["ask", "What is 2 + 2?"])

    assert result.exit_code == 0
    assert model.questions == ["What is 2 + 2?"]
    assert "Assistant>\nWhat is 2 + 2?" in result.output
