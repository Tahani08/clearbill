import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import ai_reader, tables  # noqa: F401
from app.db import Base, get_db
from app.main import app

GOOD = {
    "total": "$3,000.00",
    "items": [
        {"date": "09/14/2026", "code": "99284", "description": "Emergency room visit", "amount": "$1,850.00"},
        {"date": "09/14/2026", "code": "80048", "description": "Basic metabolic panel", "amount": "$210.00"},
        {"date": "09/14/2026", "code": "82947", "description": "Glucose test", "amount": "$45.00"},
        {"date": "09/14/2026", "code": "36415", "description": "Blood draw", "amount": "$30.00"},
        {"date": "09/14/2026", "code": "36415", "description": "Blood draw", "amount": "$30.00"},
        {"date": "09/14/2026", "code": "71046", "description": "Chest X-ray", "amount": "$400.00"},
    ],
}


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


def upload(client, content_type="image/png"):
    return client.post(
        "/bills/from-image", files={"file": ("bill.png", b"fake-image", content_type)}
    )


def test_image_upload_runs_rules(client, monkeypatch):
    monkeypatch.setattr(ai_reader, "extract_bill", lambda raw: GOOD)
    res = upload(client)
    assert res.status_code == 201
    bill = client.get(f"/bills/{res.json()['id']}").json()
    assert len(bill["items"]) == 6
    assert {f["rule"] for f in bill["flags"]} == {"math_error", "unbundling", "duplicate"}


def test_unreadable_date_is_rejected(client, monkeypatch):
    bad = {"total": "10.00", "items": [{"date": "???", "code": "1", "description": "x", "amount": "10.00"}]}
    monkeypatch.setattr(ai_reader, "extract_bill", lambda raw: bad)
    assert upload(client).status_code == 422


def test_ai_down_gives_503(client, monkeypatch):
    def boom(raw):
        raise ai_reader.AIUnavailableError("down")

    monkeypatch.setattr(ai_reader, "extract_bill", boom)
    assert upload(client).status_code == 503


def test_wrong_file_type_is_rejected(client):
    assert upload(client, "text/plain").status_code == 415