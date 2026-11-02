from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from . import ai_reader
from .db import get_db
from .extraction import to_line_items
from .parsing import BillParseError
from .storage import save_bill

router = APIRouter()

MAX_IMAGE_BYTES = 5_000_000
ALLOWED_TYPES = {"image/png", "image/jpeg"}


@router.post("/bills/from-image", status_code=201)
def upload_bill_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Please upload a PNG or JPG image")
    raw = file.file.read(MAX_IMAGE_BYTES + 1)
    if len(raw) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image is too large")

    try:
        data = ai_reader.extract_bill(raw)
        items, total_cents = to_line_items(data)
    except ai_reader.AIUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except BillParseError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return {"id": save_bill(db, items, total_cents)}