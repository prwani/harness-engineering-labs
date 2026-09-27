import json

from harness.ledger import Ledger, Usage


def test_ledger_aggregates_and_writes_provider_usage(tmp_path):
    ledger = Ledger()
    ledger.record(Usage(input_tokens=3, output_tokens=2, cached_tokens=1))
    ledger.record(Usage(input_tokens=5, cache_write_tokens=4))

    assert ledger.totals() == Usage(
        input_tokens=8, output_tokens=2, cached_tokens=1, cache_write_tokens=4
    )

    output = tmp_path / "usage.json"
    ledger.write(output)
    assert json.loads(output.read_text()) == [
        {"input_tokens": 3, "output_tokens": 2, "cached_tokens": 1, "cache_write_tokens": 0},
        {"input_tokens": 5, "output_tokens": 0, "cached_tokens": 0, "cache_write_tokens": 4},
    ]
