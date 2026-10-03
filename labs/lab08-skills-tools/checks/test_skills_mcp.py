from pathlib import Path
import sys

import pytest
from typer.testing import CliRunner

from harness.cli import learner
from harness.cli.app import app
from harness.mcp_client import MCPServer, add_server, load_servers, mcp_tools
from harness.models import ToolCall, Turn
from harness.project_skills import discover_skills, parse_skill
from harness.session import harness_home

runner = CliRunner()
ORDERS = Path(__file__).resolve().parents[1] / "orders_mcp.py"


class Recorder:
    def __init__(self, *turns):
        self.turns = iter(turns)
        self.calls = []

    def complete(self, *, system, messages, tools, **_):
        self.calls.append({"system": system, "tools": [tool["name"] for tool in tools],
                           "messages": list(messages)})
        return next(self.turns)


def make_skill(root, name="release-notes", allowed="git_cli(log *) write_file(CHANGELOG.md)"):
    path = root / name / "SKILL.md"
    path.parent.mkdir(parents=True)
    path.write_text(f"---\nname: {name}\ndescription: Draft release notes.\n"
                    f"allowed-tools: {allowed}\n---\n\n1. Run git log.\n")
    return path


def test_skill_parsing_and_discovery(tmp_path):
    skill = parse_skill(make_skill(tmp_path / ".harness" / "skills"), "project")
    assert skill.allowed_tools == ("git_cli(log *)", "write_file(CHANGELOG.md)")
    assert skill.body == "1. Run git log."
    make_skill(harness_home() / "skills", allowed="")
    make_skill(harness_home() / "skills", name="user-only", allowed="")
    skills = discover_skills(tmp_path)
    assert skills["release-notes"].scope == "project" and skills["user-only"].scope == "user"

    bad = tmp_path / "bad" / "SKILL.md"
    bad.parent.mkdir()
    bad.write_text("---\nname: bad\n---\nbody")
    with pytest.raises(ValueError, match="description"):
        parse_skill(bad, "project")


def test_model_loads_a_skill_and_its_tools_are_preapproved(tmp_path, monkeypatch):
    make_skill(tmp_path / ".harness" / "skills")
    model = Recorder(
        Turn(text="", tool_calls=[ToolCall("s", "use_skill", {"name": "release-notes"})]),
        Turn(text="", tool_calls=[ToolCall("w", "write_file", {"path": "CHANGELOG.md", "content": "## x"})]),
        Turn(text="Drafted."),
    )
    monkeypatch.setattr(learner, "create_model_client", lambda: model)

    result = runner.invoke(app, ["ask", "--repo", str(tmp_path), "What changed? Write release notes."])

    assert result.exit_code == 0, result.output
    assert "release-notes: Draft release notes." in model.calls[0]["system"]
    assert "use_skill" in model.calls[0]["tools"]
    assert "1. Run git log." in model.calls[1]["messages"][-1]["content"][0]["output"]
    assert (tmp_path / "CHANGELOG.md").read_text() == "## x"
    assert "Permission:" not in result.output


def test_slash_command_loads_the_skill_body(tmp_path, monkeypatch):
    make_skill(tmp_path / ".harness" / "skills")
    model = Recorder(Turn(text="Drafted."))
    monkeypatch.setattr(learner, "create_model_client", lambda: model)

    result = runner.invoke(app, ["ask", "--repo", str(tmp_path)],
                           input="/skills\n/release-notes since lab04-done\n/permissions\n/exit\n")

    assert result.exit_code == 0, result.output
    assert "/release-notes  [project]" in result.output
    question = model.calls[0]["messages"][-1]["content"]
    assert "1. Run git log." in question and question.endswith("since lab04-done")
    assert "allow git_cli(log *)  [skill release-notes]" in result.output


def test_mcp_server_tools(tmp_path):
    server = MCPServer("orders", [sys.executable, str(ORDERS)], tmp_path)
    try:
        tools, definitions = mcp_tools([server])
        assert sorted(tools) == ["mcp__orders__get_order", "mcp__orders__list_orders"]
        assert definitions[0]["description"].startswith("[MCP server orders]")
        assert "ORD-1004" in tools["mcp__orders__list_orders"]({"status": "cancelled"})
        with pytest.raises(RuntimeError, match="no order"):
            tools["mcp__orders__get_order"]({"order_id": "ORD-9"})
    finally:
        server.close()


def test_mcp_cli_registers_and_asks_before_a_new_tool(tmp_path, monkeypatch):
    added = runner.invoke(app, ["mcp", "add", "orders", "--repo", str(tmp_path), "--",
                                sys.executable, str(ORDERS)])
    assert added.exit_code == 0, added.output
    assert list(load_servers(tmp_path)) == ["orders"]
    listed = runner.invoke(app, ["mcp", "list", "--repo", str(tmp_path)])
    assert "mcp__orders__list_orders" in listed.output

    model = Recorder(
        Turn(text="", tool_calls=[ToolCall("o", "mcp__orders__list_orders", {"status": "pending"})]),
        Turn(text="Three pending orders."),
    )
    monkeypatch.setattr(learner, "create_model_client", lambda: model)
    result = runner.invoke(app, ["ask", "--repo", str(tmp_path)], input="Pending orders?\ny\n/mcp\n/exit\n")

    assert result.exit_code == 0, result.output
    assert "Permission: mcp__orders__list_orders" in result.output
    assert "ORD-1002" in model.calls[1]["messages"][-1]["content"][0]["output"]
    assert "mcp__orders__get_order" in result.output

    assert runner.invoke(app, ["mcp", "remove", "orders", "--repo", str(tmp_path)]).exit_code == 0
    assert runner.invoke(app, ["mcp", "remove", "orders", "--repo", str(tmp_path)]).exit_code == 1
    with pytest.raises(ValueError):
        add_server(tmp_path, "bad__name", ["x"])
