import pytest

from harness.learner import ask_with_tools
from harness.models import ScriptedModel, ToolCall, Turn
from harness.tools import build_read_only_tools


def test_read_only_tools_are_rooted_and_list_files(tmp_path):
    (tmp_path / "README.md").write_text("hello")
    tools, definitions = build_read_only_tools(tmp_path)

    assert tools["list_files"]({"path": "."}) == "README.md"
    assert {tool["name"] for tool in definitions} == set(tools)
    with pytest.raises(ValueError, match="outside"):
        tools["read_file"]({"path": "../outside.txt"})


def test_azure_tools_require_explicit_opt_in(tmp_path):
    tools, _ = build_read_only_tools(tmp_path)
    azure_tools, _ = build_read_only_tools(tmp_path, azure=True)

    assert "azure_resources" not in tools
    assert "azure_resources" in azure_tools


def test_learner_question_runs_read_tool_and_returns_answer(tmp_path):
    (tmp_path / "README.md").write_text("A sample project")
    client = ScriptedModel([
        Turn(text="", tool_calls=[ToolCall("call_1", "read_file", {"path": "README.md"})]),
        Turn(text="The README describes a sample project."),
    ])

    result = ask_with_tools(client, "Summarize README.md", repo=tmp_path)

    assert result.text == "The README describes a sample project."
