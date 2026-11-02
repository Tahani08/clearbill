from datetime import date, datetime

from .models import LineItem
from .parsing import BillParseError, dollars_to_cents


def _parse_date(text: str) -> date:
    text = text.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):  # US bills only, for now
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    raise ValueError(text)


def to_line_items(data: dict) -> tuple[list[LineItem], int]:
    raw_items = data.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        raise BillParseError("No line items were found in the image")

    items = []
    for n, raw in enumerate(raw_items, start=1):
        if not isinstance(raw, dict):
            raise BillParseError(f"Line {n}: could not be read")
        try:
            day = _parse_date(str(raw.get("date", "")))
        except ValueError:
            raise BillParseError(f"Line {n}: could not read the date")
        items.append(
            LineItem(
                n,
                day,
                str(raw.get("code", "")).strip(),
                str(raw.get("description", "")).strip(),
                dollars_to_cents(str(raw.get("amount", ""))),
            )
        )

    total_cents = dollars_to_cents(str(data.get("total", "")))
    return items, total_cents