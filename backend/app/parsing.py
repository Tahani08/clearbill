import csv
import io
from datetime import date
from decimal import Decimal, InvalidOperation

from .models import LineItem


class BillParseError(ValueError):
    """The uploaded file isn't a valid bill."""


REQUIRED_COLUMNS = {"date", "code", "description", "amount"}


def dollars_to_cents(text: str) -> int:
    """'$1,850.00' -> 185000. Decimal avoids floating-point rounding bugs."""
    cleaned = text.replace("$", "").replace(",", "").strip()
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        raise BillParseError(f"Could not read this amount: {text!r}")
    return int((value * 100).to_integral_value())


def parse_csv(text: str) -> list[LineItem]:
    reader = csv.DictReader(io.StringIO(text))
    columns = {c.strip().lower() for c in (reader.fieldnames or [])}
    if not REQUIRED_COLUMNS <= columns:
        raise BillParseError("The file needs these columns: date, code, description, amount")

    items = []
    for n, raw in enumerate(reader, start=1):
        row = {k.strip().lower(): (v or "").strip() for k, v in raw.items() if k}
        try:
            day = date.fromisoformat(row["date"])
        except ValueError:
            raise BillParseError(f"Line {n}: the date should look like 2026-09-14")
        items.append(
            LineItem(n, day, row["code"], row["description"], dollars_to_cents(row["amount"]))
        )

    if not items:
        raise BillParseError("The file has no line items")
    return items
