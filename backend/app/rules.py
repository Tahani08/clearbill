from collections import defaultdict

from .models import Bill, Flag

# ILLUSTRATIVE sample only. Later we replace this with the real public
# CMS "NCCI edits" list. (bigger code, included code) -> reason
UNBUNDLING_SAMPLE = {
    ("80048", "82947"): "A basic metabolic panel already includes a glucose test.",
    ("80053", "82947"): "A comprehensive metabolic panel already includes a glucose test.",
    ("85025", "85027"): "A CBC with differential already includes a basic CBC.",
}


def find_duplicates(bill: Bill) -> list[Flag]:
    """Same code on the same day, more than once."""
    groups = defaultdict(list)
    for item in bill.items:
        groups[(item.service_date, item.code)].append(item)

    flags = []
    for (_, code), items in groups.items():
        if len(items) > 1:
            extras = items[1:]
            flags.append(
                Flag(
                    rule="duplicate",
                    line_nos=tuple(i.line_no for i in items),
                    message=f"Code {code} appears {len(items)} times on the same day. "
                    "It may be a duplicate, or it may be legitimate. Ask the billing office.",
                    amount_at_stake_cents=sum(i.amount_cents for i in extras),
                )
            )
    return flags


def check_total(bill: Bill) -> list[Flag]:
    """Line items should add up to the stated total."""
    actual = sum(i.amount_cents for i in bill.items)
    diff = abs(actual - bill.stated_total_cents)
    if diff == 0:
        return []
    return [
        Flag(
            rule="math_error",
            line_nos=(),
            message="The line items do not add up to the total on the bill.",
            amount_at_stake_cents=diff,
        )
    ]


def find_unbundling(bill: Bill) -> list[Flag]:
    """Separately billing a test that a bigger test already includes."""
    by_day = defaultdict(lambda: defaultdict(list))
    for item in bill.items:
        by_day[item.service_date][item.code].append(item)

    flags = []
    for codes in by_day.values():
        for (big, small), reason in UNBUNDLING_SAMPLE.items():
            if big in codes and small in codes:
                small_items = codes[small]
                flags.append(
                    Flag(
                        rule="unbundling",
                        line_nos=tuple(i.line_no for i in small_items),
                        message=f"{reason} It may be billed twice. Ask if it can be removed.",
                        amount_at_stake_cents=sum(i.amount_cents for i in small_items),
                    )
                )
    return flags


def audit_bill(bill: Bill) -> list[Flag]:
    flags = find_duplicates(bill) + check_total(bill) + find_unbundling(bill)
    return sorted(flags, key=lambda f: -f.amount_at_stake_cents)