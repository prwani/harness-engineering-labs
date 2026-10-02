from typer.testing import CliRunner

from harness.cli.app import app
from harness.native_harness import FEATURE_MAP

runner = CliRunner()


def test_features_lists_every_lab_capability():
    result = runner.invoke(app, ["features"])
    assert result.exit_code == 0
    assert [row[0] for row in FEATURE_MAP][-1] == "Lab 13"
    for _, capability, command, _ in FEATURE_MAP:
        assert capability in result.output and command in result.output


def test_mapped_commands_exist():
    for command in ("ask", "sessions", "trace", "mcp", "skills", "agents", "route", "pge"):
        assert runner.invoke(app, [command, "--help"]).exit_code == 0, command
