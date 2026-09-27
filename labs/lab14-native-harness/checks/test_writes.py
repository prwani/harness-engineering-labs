import pytest

from harness.writes import WriteLog, idempotency_key, run_write


def test_idempotency_key_is_stable_regardless_of_arg_order():
    key_a = idempotency_key("update_product", {"id": "1", "price": 5})
    key_b = idempotency_key("update_product", {"price": 5, "id": "1"})

    assert key_a == key_b


def test_different_args_produce_different_keys():
    key_a = idempotency_key("update_product", {"id": "1", "price": 5})
    key_b = idempotency_key("update_product", {"id": "1", "price": 6})

    assert key_a != key_b


def test_run_write_executes_once():
    calls = []

    def tool(args):
        calls.append(args)
        return {"status": "ok"}

    log = WriteLog()
    key1, result1 = run_write(tool, "update_product", {"id": "1"}, log)
    key2, result2 = run_write(tool, "update_product", {"id": "1"}, log)

    assert len(calls) == 1
    assert key1 == key2
    assert result1 == result2 == {"status": "ok"}


def test_resume_reconciles_against_write_log_without_reexecuting():
    log = WriteLog()
    key = idempotency_key("delete_product", {"id": "3"})
    log.record(key, {"status": "deleted"})

    def tool(_args):
        raise AssertionError("should not re-run an already-applied write")

    reconciled_key, result = run_write(tool, "delete_product", {"id": "3"}, log)

    assert reconciled_key == key
    assert result == {"status": "deleted"}


def test_resume_reexecutes_a_write_with_no_persisted_result():
    log = WriteLog()

    def tool(args):
        return {"status": "created", "id": args["id"]}

    key, result = run_write(tool, "create_product", {"id": "4"}, log)

    assert log.applied(key)
    assert result == {"status": "created", "id": "4"}
