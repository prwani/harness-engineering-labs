from typer.testing import CliRunner

from harness.cli import learner
from harness.cli.app import app
from harness.learner import ask_with_tools
from harness.models import Turn
from harness.project_memory import INIT_PROMPT, MAX_MEMORY_CHARS, load_memory, memory_prompt
from harness.session import harness_home

runner = CliRunner()


class Recorder:
    def __init__(self, text="ok"):
        self.text = text
        self.calls = []

    def complete(self, *, system, messages, **_):
        self.calls.append({"system": system, "last": messages[-1]["content"]})
        return Turn(text=self.text)


def test_memory_files_load_broadest_first(tmp_path):
    harness_home().mkdir(parents=True, exist_ok=True)
    (harness_home() / "HARNESS.md").write_text("user rule")
    (tmp_path / "HARNESS.md").write_text("project rule")
    (tmp_path / "HARNESS.local.md").write_text("local rule")

    files = load_memory(tmp_path)

    assert [item.scope for item in files] == ["user", "project", "local"]
    prompt = memory_prompt(files)
    assert prompt.index("user rule") < prompt.index("project rule") < prompt.index("local rule")


def test_missing_empty_and_oversized_memory(tmp_path):
    assert load_memory(tmp_path) == [] and memory_prompt([]) == ""
    (tmp_path / "HARNESS.local.md").write_text("   \n")
    (tmp_path / "HARNESS.md").write_text("x" * (MAX_MEMORY_CHARS + 10))

    [item] = load_memory(tmp_path)

    assert item.truncated and len(item.text) == MAX_MEMORY_CHARS
    assert "(truncated)" in memory_prompt([item])


def test_memory_is_reread_for_every_question(tmp_path):
    model = Recorder()
    (tmp_path / "HARNESS.md").write_text("- Money is integer cents.")
    ask_with_tools(model, "one", repo=tmp_path)
    (tmp_path / "HARNESS.md").write_text("- Money is integer cents.\n- Every public function has a docstring.")
    ask_with_tools(model, "two", repo=tmp_path)

    assert "integer cents" in model.calls[0]["system"]
    assert "docstring" not in model.calls[0]["system"]
    assert "docstring" in model.calls[1]["system"]


def test_cli_memory_and_init(tmp_path, monkeypatch):
    model = Recorder("Wrote HARNESS.md.")
    monkeypatch.setattr(learner, "create_model_client", lambda: model)
    (tmp_path / "HARNESS.md").write_text("line one\nline two")

    result = runner.invoke(app, ["ask", "--repo", str(tmp_path)], input="/memory\n/init Mention cents.\n/exit\n")

    assert result.exit_code == 0, result.output
    assert "project" in result.output and "(2 lines)" in result.output
    assert "local" in result.output and "not found" in result.output
    assert model.calls[0]["last"] == f"{INIT_PROMPT} Mention cents."

    files = runner.invoke(app, ["memory", "files", "--repo", str(tmp_path)])
    assert "(2 lines)" in files.output
