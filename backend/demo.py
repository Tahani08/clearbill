from datetime import date

from app.models import Bill, LineItem
from app.rules import audit_bill

d = date(2026, 9, 14)
bill = Bill(
    items=[
        LineItem(1, d, "99284", "Emergency room visit", 185000),
        LineItem(2, d, "80048", "Basic metabolic panel", 21000),
        LineItem(3, d, "82947", "Glucose test", 4500),
        LineItem(4, d, "36415", "Blood draw", 3000),
        LineItem(5, d, "36415", "Blood draw", 3000),
        LineItem(6, d, "71046", "Chest X-ray", 40000),
    ],
    stated_total_cents=300000,
)

for f in audit_bill(bill):
    print(f"[{f.rule}] lines {f.line_nos}: ${f.amount_at_stake_cents / 100:,.2f}")
    print(f"   {f.message}\n")