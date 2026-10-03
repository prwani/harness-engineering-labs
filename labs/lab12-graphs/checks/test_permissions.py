import json

import pytest
from typer.testing import CliRunner

from harness.approval import Decision
from harness.cli import learner
from harness.cli.app import app
from harness.learner import ask_with_tools
from harness.models import ToolCall, Turn
from harness.permissions import PermissionRule, Permissions, subject
from harness.session import harness_home

runner = CliRunner()


def settings(path, **permissions):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"permissions": permissions}))


class Scripted:
    def __init__(self, *turns):
        self.turns = iter(turns)

    def complete(self, **_):
        return next(self.turns)


def write_call(path="notes.txt"):
    return Turn(text="", tool_calls=[ToolCall("w", "write_file", {"path": path, "content": "hi"})])


def test_rules_parse_and_match_subjects(tmp_path):
    rule = PermissionRule.parse("git_cli(commit *)", Decision.ASK, "test")
    assert rule.matches("git_cli", subject(tmp_path, "git_cli", {"args": ["commit", "-m", "x"]}))
    assert not rule.matches("git_cli", "status")
    assert subject(tmp_path, "read_file", {"path": "./sub/../.env"}) == ".env"
    assert PermissionRule.parse("run_tests", Decision.ALLOW, "test").matches("run_tests", "{}")
    with pytest.raises(ValueError):
        PermissionRule.parse("read_file(.env", Decision.DENY, "test")


def test_deny_beats_ask_beats_allow_and_defaults(tmp_path):
    settings(tmp_path / ".harness" / "settings.json",
             allow=["read_file", "git_cli(commit *)"], ask=["git_cli(commit *)"], deny=["read_file(.env*)"])
    permissions = Permissions.load(tmp_path)

    assert permissions.decide("read_file", {"path": ".env"})[0] is Decision.DENY
    assert permissions.decide("read_file", {"path": "app.py"})[0] is Decision.ALLOW
    assert permissions.decide("git_cli", {"args": ["commit", "-m", "x"]})[0] is Decision.ASK
    assert permissions.decide("git_cli", {"args": ["diff"]})[0] is Decision.ALLOW
    assert permissions.decide("git_cli", {"args": ["mv", "catalog.csv", "x.csv"]})[0] is Decision.ASK
    assert permissions.decide("write_file", {"path": "a.py"})[0] is Decision.ASK
    assert Permissions.load(tmp_path, accept_edits=True).decide("write_file", {"path": "a.py"})[0] is Decision.ALLOW


def test_user_project_and_local_settings_merge(tmp_path):
    settings(harness_home() / "settings.json", deny=["git_cli(push*)"])
    settings(tmp_path / ".harness" / "settings.json", ask=["git_cli(commit *)"])
    settings(tmp_path / ".harness" / "settings.local.json", allow=["git_cli(tag *)"])

    text = Permissions.load(tmp_path).describe()

    assert "deny  git_cli(push*)  [user" in text
    assert "ask   git_cli(commit *)  [project" in text
    assert "allow git_cli(tag *)  [local" in text


def test_always_is_remembered_for_the_session_but_not_for_ask_rules(tmp_path):
    settings(tmp_path / ".harness" / "settings.json", ask=["git_cli(commit *)"])
    permissions, asked, events = Permissions.load(tmp_path), [], []
    hook = permissions.hook(lambda tool, args, why: asked.append(tool) or "a",
                            lambda *event: events.append(event))

    assert hook("write_file", {"path": "a.py"}).allowed
    assert hook("write_file", {"path": "a.py"}).allowed
    assert hook("git_cli", {"args": ["commit", "-m", "x"]}).allowed
    assert hook("git_cli", {"args": ["commit", "-m", "x"]}).allowed
    assert asked == ["write_file", "git_cli", "git_cli"]
    assert events[1][3] == "approved always for this session"

    no_one = Permissions.load(tmp_path).hook()
    decision = no_one("write_file", {"path": "a.py"})
    assert not decision.allowed and "no one to approve" in decision.reason


def test_declined_write_does_not_run(tmp_path):
    permissions, denials = Permissions.load(tmp_path), []
    ask_with_tools(Scripted(write_call(), Turn(text="ok")), "write", repo=tmp_path,
                   permissions=permissions, approver=lambda *_: "n",
                   on_hook_denial=lambda name, reason: denials.append(reason))

    assert not (tmp_path / "notes.txt").exists()
    assert "permission denied" in denials[0] and "human answered no" in denials[0]


def test_cli_prompts_and_writes_after_yes(tmp_path, monkeypatch):
    monkeypatch.setattr(learner, "create_model_client", lambda: Scripted(write_call(), Turn(text="done")))

    result = runner.invoke(app, ["ask", "--repo", str(tmp_path)], input="write it\ny\n/permissions\n/exit\n")

    assert result.exit_code == 0, result.output
    assert "Permission: write_file(notes.txt) [default: ask]" in result.output
    assert (tmp_path / "notes.txt").read_text() == "hi"
    assert "Defaults:" in result.output


def test_cli_one_shot_without_input_denies(tmp_path, monkeypatch):
    monkeypatch.setattr(learner, "create_model_client", lambda: Scripted(write_call(), Turn(text="denied")))

    result = runner.invoke(app, ["ask", "--repo", str(tmp_path), "write it"])

    assert result.exit_code == 0, result.output
    assert not (tmp_path / "notes.txt").exists()


def test_accept_edits_skips_the_prompt(tmp_path, monkeypatch):
    monkeypatch.setattr(learner, "create_model_client", lambda: Scripted(write_call(), Turn(text="done")))

    result = runner.invoke(app, ["ask", "--repo", str(tmp_path), "--accept-edits", "write it"])

    assert "Permission:" not in result.output
    assert (tmp_path / "notes.txt").exists()


def test_permissions_command(tmp_path):
    settings(tmp_path / ".harness" / "settings.json", deny=["read_file(.env)"])

    result = runner.invoke(app, ["permissions", "--repo", str(tmp_path)])

    assert "deny  read_file(.env)" in result.output
