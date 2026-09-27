import pytest

from harness.planning import EXECUTOR, PLANNER, ModeSwitch, has_write_tools
from harness.todos import TodoList


def test_planner_has_no_write_tools():
    assert not has_write_tools(PLANNER)
    assert has_write_tools(EXECUTOR)


def test_only_harness_switches_mode():
    switch = ModeSwitch()
    assert switch.mode == "plan"
    assert switch.spec is PLANNER

    spec = switch.switch("execute")

    assert spec is EXECUTOR
    assert switch.mode == "execute"


def test_switching_to_unknown_mode_fails():
    with pytest.raises(ValueError, match="unknown mode"):
        ModeSwitch().switch("delete-everything")


def test_todos_are_reinjected_every_turn():
    todos = TodoList()
    todos.write(["fix price", "restock treats"])

    assert todos.reminder() == "Open todos:\n- fix price\n- restock treats"

    todos.complete("fix price")

    assert todos.reminder() == "Open todos:\n- restock treats"
    assert [item.text for item in todos.open] == ["restock treats"]


def test_completing_unknown_todo_fails():
    todos = TodoList()
    todos.write(["fix price"])

    with pytest.raises(ValueError, match="no such todo"):
        todos.complete("missing")


def test_empty_todo_list_has_no_reminder():
    assert TodoList().reminder() is None
