from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from . import tables
from .db import Base, engine, get_db
from .models import Bill, LineItem
from .parsing import BillParseError, dollars_to_cents, parse_csv
from .rules import audit_bill

app = FastAPI(title="ClearBill API")
Base.metadata.create_all(engine)

MAX_UPLOAD_BYTES = 1_000_000


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/bills", status_code=201)
async def upload_bill(
    file: UploadFile = File(...),
    stated_total: str = Form(...),
    db: Session = Depends(get_db),
):
    raw = await file.read()
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File is too large")
    try:
        items = parse_csv(raw.decode("utf-8-sig"))
        total_cents = dollars_to_cents(stated_total)
    except UnicodeDecodeError:
        raise HTTPException(status_code=422, detail="File must be a UTF-8 text CSV")
    except BillParseError as e:
        raise HTTPException(status_code=422, detail=str(e))

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
    return {"id": bill.id}


@app.get("/bills/{bill_id}")
def get_bill(bill_id: int, db: Session = Depends(get_db)):
    row = db.get(tables.BillRow, bill_id)
    if not row:
        raise HTTPException(status_code=404, detail="Bill not found")

    items = [
        LineItem(r.line_no, r.service_date, r.code, r.description, r.amount_cents)
        for r in row.items
    ]
    # Flags are computed fresh each time, so rule improvements apply to old bills too.
    flags = audit_bill(Bill(items, row.stated_total_cents))

    return {
        "id": row.id,
        "stated_total_cents": row.stated_total_cents,
        "items": [
            {
                "line_no": i.line_no,
                "service_date": i.service_date.isoformat(),
                "code": i.code,
                "description": i.description,
                "amount_cents": i.amount_cents,
            }
            for i in items
        ],
        "flags": [
            {
                "rule": f.rule,
                "line_nos": list(f.line_nos),
                "message": f.message,
                "amount_at_stake_cents": f.amount_at_stake_cents,
            }
            for f in flags
        ],
    }