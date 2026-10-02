from pathlib import Path

from harness.agents import parse_agent
from harness.tools import build_tools

ASSETS = Path(__file__).resolve().parents[1] / "assets" / ".harness" / "agents"


def test_lab_agents_use_real_tool_names(tmp_path):
    _, definitions = build_tools(tmp_path)
    names = {item["name"] for item in definitions}
    reviewer = parse_agent(ASSETS / "security-reviewer.md", "project")
    writer = parse_agent(ASSETS / "test-writer.md", "project")
    assert set(reviewer.tools) <= names and set(writer.tools) <= names
    assert not any(reviewer.allows(tool) for tool in ("write_file", "edit_file", "git_cli", "shell"))
    assert writer.allows("write_file") and writer.allows("run_tests") and not writer.allows("git_cli")
