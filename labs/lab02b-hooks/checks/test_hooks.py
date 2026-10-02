import pytest

import json
import sys

from harness.hooks import (
    HookPipeline, ToolDecision, command_policy, load_project_hooks, load_rules, validate_history,
)
from harness.models import ScriptedModel, ToolCall, Turn
from harness.tool_loop import run_tool_loop
from harness.tools import build_tools

SHELL_DENIAL = "shell commands are disabled; use run_tests, git_cli, and file tools"


def test_builtin_policy_allows_everyday_git_and_denies_destructive_commands():
    for args in (["status"], ["log", "-1", "--oneline"], ["add", "."], ["commit", "-m", "x"],
                 ["switch", "-c", "feature"], ["merge", "feature"], ["revert", "HEAD"]):
        assert command_policy("git_cli", {"args": args}).allowed, args
    assert command_policy("azure_cli", {"args": ["account", "show"]}).allowed
    assert command_policy("azure_cli", {"args": ["resource", "list"]}).allowed
    assert command_policy("write_file", {"path": "app.py", "content": ""}).allowed
    for args in (["reset", "--hard"], ["rm", "README.md"], ["push"], ["clean", "-fd"],
                 ["-c", "core.hooksPath=x", "commit"], []):
        assert not command_policy("git_cli", {"args": args}).allowed, args
    assert not command_policy("azure_cli", {"args": ["group", "delete"]}).allowed
    assert not command_policy("shell", {"command": "echo hello"}).allowed


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
    assert denied == [("shell", SHELL_DENIAL)]
    assert calls[1]["messages"][-1]["content"] == [
        {"call_id": "blocked", "output": f"DENIED: {SHELL_DENIAL}"},
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
        "output": "DENIED: git rm is denied by the built-in policy",
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


def _project(tmp_path, settings=None, hooks=None, rules=None):
    harness_dir = tmp_path / ".harness"
    (harness_dir / "hooks").mkdir(parents=True)
    (harness_dir / "rules").mkdir()
    if settings is not None:
        (harness_dir / "settings.json").write_text(json.dumps(settings))
    for name, body in (hooks or {}).items():
        (harness_dir / "hooks" / name).write_text(body)
    for name, body in (rules or {}).items():
        (harness_dir / "rules" / name).write_text(body)
    return tmp_path


BLOCK_CSV = """import json, sys
call = json.load(sys.stdin)
if call["args"].get("path", "").endswith("catalog.csv"):
    print("catalog.csv is protected", file=sys.stderr)
    sys.exit(2)
"""

FAIL_AFTER_EDIT = """import json, sys
call = json.load(sys.stdin)
print("tests failed after " + call["args"]["path"], file=sys.stderr)
sys.exit(2)
"""


def test_project_pre_tool_hook_blocks_matching_call_before_execution(tmp_path):
    root = _project(
        tmp_path,
        settings={"hooks": {"pre_tool": [
            {"matcher": "write_file|edit_file", "command": ["python", ".harness/hooks/block.py"]},
        ]}},
        hooks={"block.py": BLOCK_CSV},
    )
    (root / "catalog.csv").write_text("sku,price_cents\nP1,100\n")
    tools, definitions = build_tools(root)
    model = ScriptedModel([
        Turn(text="", tool_calls=[
            ToolCall("csv", "write_file", {"path": "catalog.csv", "content": "changed"}),
            ToolCall("py", "write_file", {"path": "notes.py", "content": "x = 1\n"}),
        ]),
        Turn(text="done"),
    ])
    denied = []

    run_tool_loop(model, "task", "system", tools, tool_definitions=definitions,
                  hooks=load_project_hooks(root), on_hook_denial=lambda *d: denied.append(d))

    assert denied == [("write_file", "catalog.csv is protected")]
    assert (root / "catalog.csv").read_text() == "sku,price_cents\nP1,100\n"
    assert (root / "notes.py").read_text() == "x = 1\n"


def test_project_post_tool_hook_feedback_reaches_model_and_learner(tmp_path):
    root = _project(
        tmp_path,
        settings={"hooks": {"post_tool": [
            {"matcher": "edit_file", "command": [sys.executable, ".harness/hooks/fail.py"]},
        ]}},
        hooks={"fail.py": FAIL_AFTER_EDIT},
    )
    (root / "pricing.py").write_text("TAX = 1\n")
    tools, definitions = build_tools(root)

    class RecordingModel(ScriptedModel):
        def __init__(self):
            super().__init__([
                Turn(text="", tool_calls=[ToolCall("edit", "edit_file", {
                    "path": "pricing.py", "old_text": "TAX = 1", "new_text": "TAX = 2"})]),
                Turn(text="I will fix the failure."),
            ])
            self.calls = []

        def complete(self, **kwargs):
            self.calls.append(kwargs)
            return super().complete(**kwargs)

    model = RecordingModel()
    feedback = []
    run_tool_loop(model, "task", "system", tools, tool_definitions=definitions,
                  hooks=load_project_hooks(root, lambda *f: feedback.append(f)))

    output = model.calls[1]["messages"][-1]["content"][0]["output"]
    assert output.startswith("Edited pricing.py.")
    assert "tests failed after pricing.py" in output
    assert feedback == [("edit_file", "tests failed after pricing.py")]


def test_scoped_rule_is_added_once_and_only_for_matching_paths(tmp_path):
    root = _project(tmp_path, rules={
        "pricing.md": '---\npaths:\n  - "pricing.py"\n---\nUse integer cents.\n',
        "docs.md": "---\npaths: docs/*.md, README.md\n---\nKeep docs short.\n",
    })
    (root / "pricing.py").write_text("TAX = 1\n")
    (root / "inventory.py").write_text("ITEMS = {}\n")
    rules = {rule.name: rule.paths for rule in load_rules(root)}
    assert rules == {"docs.md": ("docs/*.md", "README.md"), "pricing.md": ("pricing.py",)}

    loaded = []
    pipeline = load_project_hooks(root, lambda *f: loaded.append(f))
    first = pipeline.after_tool("read_file", {"path": "pricing.py"}, "TAX = 1")
    second = pipeline.after_tool("read_file", {"path": "pricing.py"}, "TAX = 1")
    other = pipeline.after_tool("read_file", {"path": "inventory.py"}, "ITEMS = {}")

    assert "Project rule pricing.md applies to pricing.py:\nUse integer cents." in first
    assert second == "TAX = 1" and other == "ITEMS = {}"
    assert loaded == [("read_file", "loaded rule pricing.md for pricing.py")]


def test_project_without_harness_settings_has_no_extra_hooks(tmp_path):
    pipeline = load_project_hooks(tmp_path)

    assert pipeline.pre_tool == () and pipeline.post_tool == ()


def test_invalid_project_settings_fail_clearly(tmp_path):
    root = _project(tmp_path)
    (root / ".harness" / "settings.json").write_text("{not json")

    with pytest.raises(ValueError, match="Invalid"):
        load_project_hooks(root)

