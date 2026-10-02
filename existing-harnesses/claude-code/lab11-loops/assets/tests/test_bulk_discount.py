"""Acceptance tests for Lab 11. Do not edit; make them pass."""
import pytest

from pricing import bulk_discount_percent


@pytest.mark.parametrize(
    "qty, expected",
    [(1, 0), (9, 0), (10, 5), (49, 5), (50, 10), (500, 10)],
)
def test_bulk_discount_tiers(qty, expected):
    assert bulk_discount_percent(qty) == expected


@pytest.mark.parametrize("qty", [0, -1])
def test_bulk_discount_rejects_non_positive_quantity(qty):
    with pytest.raises(ValueError):
        bulk_discount_percent(qty)
