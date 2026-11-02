from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class BillRow(Base):
    __tablename__ = "bills"

    id: Mapped[int] = mapped_column(primary_key=True)
    stated_total_cents: Mapped[int]
    items: Mapped[list["ItemRow"]] = relationship(
        back_populates="bill",
        cascade="all, delete-orphan",
        order_by="ItemRow.line_no",
    )


class ItemRow(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    bill_id: Mapped[int] = mapped_column(ForeignKey("bills.id"), index=True)
    line_no: Mapped[int]
    service_date: Mapped[date] = mapped_column(Date)
    code: Mapped[str] = mapped_column(String(20))
    description: Mapped[str] = mapped_column(String(200))
    amount_cents: Mapped[int]
    bill: Mapped[BillRow] = relationship(back_populates="items")
