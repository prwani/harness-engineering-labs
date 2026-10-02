import pytest

from harness.hooks import HookPipeline, ToolDecision, read_command_policy, validate_history
from harness.models import ScriptedModel, ToolCall, Turn
from harness.tool_loop import run_tool_loop
from harness.tools import build_tools


def test_demo_policy_allows_exact_reads_and_denies_other_commands():
    assert read_command_policy("git_cli", {"args": ["status"]}).allowed
    assert read_command_policy("git_cli", {"args": ["log", "-1", "--oneline"]}).allowed
    assert read_command_policy("azure_cli", {"args": ["account", "show"]}).allowed
    assert read_command_policy("azure_cli", {"args": ["resource", "list"]}).allowed
    assert not read_command_policy("git_cli", {"args": ["reset", "--hard"]}).allowed
    assert not read_command_policy("azure_cli", {"args": ["group", "delete"]}).allowed
    assert not read_command_policy("shell", {"command": "echo hello"}).allowed


def test_denied_call_is_not_executed_and_still_gets_correlated_result():
    calls = []

    class RecordingModel(ScriptedModel):
        def complete(self, **kwargs):
            calls.append(kwargs)
            return super().complete(**kwargs)

    client = RecordingModel([
        Turn(text="", tool_calls=[
            ToolCall("blocked", "shell", {"command": "echo hello"}),
            ToolCall("allowed", "git_cli", {"args": ["status"]}),
        ]),
        Turn(text="done"),
    ])
    executed = []
    denied = []
    result = run_tool_loop(
        client, "task", "system",
        {"shell": lambda args: executed.append("shell"),
         "git_cli": lambda args: executed.append("git") or "status result"},
        on_hook_denial=lambda name, reason: denied.append((name, reason)),
    )

    assert result.text == "done"
    assert executed == ["git"]
    assert denied == [("shell", "shell commands are disabled in Lab 2B")]
    assert calls[1]["messages"][-1]["content"] == [
        {"call_id": "blocked", "output": "DENIED: shell commands are disabled in Lab 2B"},
        {"call_id": "allowed", "output": "status result"},
    ]
    assert "call_ids" not in calls[1]["messages"][-2]


def test_git_rm_is_denied_and_disposable_file_remains(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("Disposable file")
    tools, definitions = build_tools(tmp_path)

    class RecordingModel(ScriptedModel):
        def __init__(self):
            super().__init__([
                Turn(text="", tool_calls=[
                    ToolCall("remove-readme", "git_cli", {"args": ["rm", "README.md"]}),
                ]),
                Turn(text="The removal was denied."),
            ])
            self.calls = []

        def complete(self, **kwargs):
            self.calls.append(kwargs)
            return super().complete(**kwargs)

    model = RecordingModel()
    result = run_tool_loop(
        model, "Remove README.md", "system", tools, tool_definitions=definitions
    )

    assert result.text == "The removal was denied."
    assert model.calls[1]["messages"][-1]["content"] == [{
        "call_id": "remove-readme",
        "output": "DENIED: git_cli permits only status or log -1 --oneline",
    }]
    assert readme.read_text() == "Disposable file"


def test_extra_hook_can_only_tighten_default_policy():
    calls = []
    client = ScriptedModel([
        Turn(text="", tool_calls=[ToolCall("one", "git_cli", {"args": ["status"]})]),
        Turn(text="done"),
    ])
    result = run_tool_loop(
        client, "task", "system", {"git_cli": lambda _: calls.append("ran")},
        hooks=HookPipeline(pre_tool=(lambda *_: ToolDecision(False, "blocked by extra hook"),)),
    )
    assert result.text == "done"
    assert calls == []


def test_extra_allow_cannot_override_builtin_denial():
    client = ScriptedModel([
        Turn(text="", tool_calls=[ToolCall("one", "shell", {"command": "echo demo"})]),
        Turn(text="denied"),
    ])
    result = run_tool_loop(
        client, "task", "system", {"shell": lambda _: pytest.fail("executed")},
        hooks=HookPipeline(pre_tool=(lambda *_: ToolDecision(True),)),
    )
    assert result.text == "denied"


def test_pre_model_rejects_unpaired_history():
    with pytest.raises(ValueError, match="same ID"):
        validate_history([
            {"role": "user", "content": "task"},
            {"role": "assistant", "call_ids": ["one", "two"]},
            {"role": "tool", "content": [{"call_id": "one"}, {"call_id": "one"}]},
        ])


def test_duplicate_call_ids_fail_before_execution():
    client = ScriptedModel([Turn(text="", tool_calls=[
        ToolCall("same", "git_cli", {"args": ["status"]}),
        ToolCall("same", "git_cli", {"args": ["status"]}),
    ])])
    with pytest.raises(ValueError, match="unique"):
        run_tool_loop(client, "task", "system", {"git_cli": lambda _: pytest.fail("executed")})
