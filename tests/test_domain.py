"""Unit tests for services.inventory.domain (no database)."""

import uuid

import pytest
from services.inventory.domain import (
    WarehouseQuantity,
    aggregate_stock,
    normalize_unit,
    validate_reorder_level,
)


def test_aggregate_stock_empty_returns_zero_and_below_reorder() -> None:
    iid = uuid.uuid4()
    summary = aggregate_stock(iid, 10.0, [])
    assert summary.total_quantity == 0.0
    assert summary.is_below_reorder is True
    assert summary.per_warehouse == ()


def test_aggregate_stock_sums_warehouses_and_flags_above_reorder() -> None:
    iid = uuid.uuid4()
    w1, w2 = uuid.uuid4(), uuid.uuid4()
    rows = (
        WarehouseQuantity(w1, 30.0),
        WarehouseQuantity(w2, 25.0),
    )
    summary = aggregate_stock(iid, 50.0, rows)
    assert summary.total_quantity == 55.0
    assert summary.is_below_reorder is False
    assert len(summary.per_warehouse) == 2


def test_aggregate_stock_merges_same_warehouse() -> None:
    iid = uuid.uuid4()
    w1 = uuid.uuid4()
    rows = (WarehouseQuantity(w1, 10.0), WarehouseQuantity(w1, 5.0))
    summary = aggregate_stock(iid, 100.0, rows)
    assert summary.total_quantity == 15.0
    assert len(summary.per_warehouse) == 1
    assert summary.per_warehouse[0].quantity == 15.0


def test_aggregate_stock_exact_threshold_is_not_below() -> None:
    iid = uuid.uuid4()
    w1 = uuid.uuid4()
    summary = aggregate_stock(iid, 10.0, (WarehouseQuantity(w1, 10.0),))
    assert summary.total_quantity == 10.0
    assert summary.is_below_reorder is False


def test_aggregate_stock_negative_quantity_raises() -> None:
    iid = uuid.uuid4()
    w1 = uuid.uuid4()
    with pytest.raises(ValueError, match="negative"):
        aggregate_stock(iid, 1.0, (WarehouseQuantity(w1, -1.0),))


def test_normalize_unit_lowercases_and_strips() -> None:
    assert normalize_unit("  KG ") == "kg"


def test_normalize_unit_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="unit must be one of"):
        normalize_unit("tons")


def test_validate_reorder_level_negative_rejected() -> None:
    with pytest.raises(ValueError, match="reorder_level"):
        validate_reorder_level(-0.01)


def test_validate_reorder_level_zero_ok() -> None:
    assert validate_reorder_level(0.0) == 0.0
