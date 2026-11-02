import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import tables  # noqa: F401  (registers the tables)
from app.db import Base, get_db
from app.main import app
from app.parsing import dollars_to_cents

CSV = """date,code,description,amount
2026-09-14,99284,Emergency room visit,"1,850.00"
2026-09-14,80048,Basic metabolic panel,210.00
2026-09-14,82947,Glucose test,45.00
2026-09-14,36415,Blood draw,30.00
2026-09-14,36415,Blood draw,30.00
2026-09-14,71046,Chest X-ray,400.00
"""


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine, expire_on_commit=False)

    def override():
        with Session() as db:
            yield db

    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_upload_then_audit(client):
    res = client.post(
        "/bills",
        files={"file": ("bill.csv", CSV, "text/csv")},
        data={"stated_total": "3000.00"},
    )
    assert res.status_code == 201

    bill = client.get(f"/bills/{res.json()['id']}").json()
    assert len(bill["items"]) == 6
    assert {f["rule"] for f in bill["flags"]} == {"math_error", "unbundling", "duplicate"}


def test_bad_csv_is_rejected(client):
    res = client.post(
        "/bills",
        files={"file": ("bad.csv", "not,a,bill\n1,2,3\n", "text/csv")},
        data={"stated_total": "100"},
    )
    assert res.status_code == 422


def test_missing_bill_is_404(client):
    assert client.get("/bills/999").status_code == 404


def test_money_parsing():
    assert dollars_to_cents("$1,850.00") == 185000
    assert dollars_to_cents("0.10") == 10