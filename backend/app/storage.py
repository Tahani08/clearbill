from sqlalchemy.orm import Session

from . import tables
from .models import LineItem


def save_bill(db: Session, items: list[LineItem], total_cents: int) -> int:
    bill = tables.BillRow(
        stated_total_cents=total_cents,
        items=[
            tables.ItemRow(
                line_no=i.line_no,
                service_date=i.service_date,
                code=i.code,
                description=i.description,
                amount_cents=i.amount_cents,
            )
            for i in items
        ],
    )
    db.add(bill)
    db.commit()
    return bill.id