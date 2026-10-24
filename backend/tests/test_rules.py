from datetime import date

from app.models import Bill, LineItem
from app.rules import audit_bill, check_total, find_duplicates, find_unbundling

D = date(2026, 9, 14)


def item(n, code, cents, day=D):
    return LineItem(n, day, code, "test", cents)


def test_duplicate_detected():
    bill = Bill([item(1, "36415", 3000), item(2, "36415", 3000)], 6000)
    flags = find_duplicates(bill)
    assert len(flags) == 1
    assert flags[0].amount_at_stake_cents == 3000


def test_same_code_different_days_is_not_duplicate():
    bill = Bill(
        [item(1, "36415", 3000), item(2, "36415", 3000, date(2026, 9, 15))], 6000
    )
    assert find_duplicates(bill) == []


def test_total_mismatch_detected():
    bill = Bill([item(1, "99284", 100000)], 105000)
    assert check_total(bill)[0].amount_at_stake_cents == 5000


def test_total_matches_no_flag():
    bill = Bill([item(1, "99284", 100000)], 100000)
    assert check_total(bill) == []


def test_unbundling_detected():
    bill = Bill([item(1, "80048", 21000), item(2, "82947", 4500)], 25500)
    flags = find_unbundling(bill)
    assert len(flags) == 1
    assert flags[0].line_nos == (2,)


def test_clean_bill_has_no_flags():
    bill = Bill([item(1, "99284", 100000), item(2, "71046", 40000)], 140000)
    assert audit_bill(bill) == []