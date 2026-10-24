from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class LineItem:
    line_no: int
    service_date: date
    code: str  # billing code, e.g. "80048"
    description: str
    amount_cents: int  # money as whole cents avoids rounding bugs


@dataclass
class Bill:
    items: list[LineItem]
    stated_total_cents: int


@dataclass(frozen=True)
class Flag:
    rule: str
    line_nos: tuple[int, ...]
    message: str
    amount_at_stake_cents: int