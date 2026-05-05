"""Pure business rules for inventory (no I/O)."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

ALLOWED_UNITS = frozenset({"kg", "g", "l", "ml", "pcs"})


@dataclass(frozen=True)
class WarehouseQuantity:
    warehouse_id: UUID
    quantity: float


@dataclass(frozen=True)
class IngredientStockSummary:
    ingredient_id: UUID
    total_quantity: float
    reorder_level: float
    is_below_reorder: bool
    per_warehouse: tuple[WarehouseQuantity, ...]


def validate_reorder_level(value: float) -> float:
    if value < 0:
        msg = "reorder_level must be >= 0"
        raise ValueError(msg)
    return value


def normalize_unit(raw: str) -> str:
    u = raw.strip().lower()
    if u not in ALLOWED_UNITS:
        msg = f"unit must be one of {sorted(ALLOWED_UNITS)}"
        raise ValueError(msg)
    return u


def aggregate_stock(
    ingredient_id: UUID,
    reorder_level: float,
    rows: Iterable[WarehouseQuantity],
) -> IngredientStockSummary:
    """Sum quantity per warehouse, then total; below reorder when total < reorder_level."""
    validate_reorder_level(reorder_level)
    by_wh: defaultdict[UUID, float] = defaultdict(float)
    for row in rows:
        if row.quantity < 0:
            msg = "stock quantity cannot be negative"
            raise ValueError(msg)
        by_wh[row.warehouse_id] += row.quantity
    per = tuple(
        WarehouseQuantity(wid, qty)
        for wid, qty in sorted(by_wh.items(), key=lambda t: str(t[0]))
    )
    total = sum(by_wh.values(), start=0.0)
    is_below = total < reorder_level
    return IngredientStockSummary(
        ingredient_id=ingredient_id,
        total_quantity=total,
        reorder_level=reorder_level,
        is_below_reorder=is_below,
        per_warehouse=per,
    )
