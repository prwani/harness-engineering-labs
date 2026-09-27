import pytest

from harness.subagents import (
    ConcurrencyCapError,
    FanOutPlan,
    make_task,
    run_fan_out,
    run_sub_agent,
)


def test_sub_agent_gets_an_isolated_transcript():
    seen_transcripts = []

    def runner(task, transcript):
        seen_transcripts.append(list(transcript.messages))
        return f"done: {task.description}"

    task = make_task("map service A")
    result = run_sub_agent(task, runner)

    assert result.output == "done: map service A"
    assert seen_transcripts[0] == [{"role": "user", "content": "map service A"}]


def test_fan_out_runs_every_independent_task():
    plan = FanOutPlan(concurrency_cap=2)
    plan.add(make_task("map service A"))
    plan.add(make_task("map service B"))
    plan.add(make_task("map service C"))

    def runner(task, _transcript):
        return task.description

    results = run_fan_out(plan, runner)

    assert {result.output for result in results} == {
        "map service A", "map service B", "map service C",
    }


def test_fan_out_batches_respect_the_concurrency_cap():
    plan = FanOutPlan(concurrency_cap=2)
    for index in range(5):
        plan.add(make_task(f"task-{index}"))

    batches = plan.batches()

    assert [len(batch) for batch in batches] == [2, 2, 1]


def test_child_transcripts_never_leak_into_each_other():
    transcripts = []

    def runner(task, transcript):
        transcripts.append(transcript)
        return "ok"

    plan = FanOutPlan(concurrency_cap=4)
    plan.add(make_task("A"))
    plan.add(make_task("B"))

    run_fan_out(plan, runner)

    task_ids = {transcript.task_id for transcript in transcripts}
    assert len(task_ids) == 2
    for transcript in transcripts:
        assert len(transcript.messages) == 2


def test_requesting_more_parallel_spawns_than_the_cap_fails():
    plan = FanOutPlan(concurrency_cap=2)

    with pytest.raises(ConcurrencyCapError):
        plan.check_cap(3)
