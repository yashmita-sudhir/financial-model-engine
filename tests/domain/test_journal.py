from decimal import Decimal

import pytest
from pydantic import ValidationError

from financial_model_engine.domain import JournalEntry, JournalEntryLine


def _entry(lines):
    return JournalEntry(
        id="je1", description="Seed funding", period_id="2027-01", lines=lines
    )


def test_balanced_entry_accepted():
    entry = _entry(
        [
            JournalEntryLine(account_id="cash", debit=Decimal("50000")),
            JournalEntryLine(
                account_id="contributed_equity", credit=Decimal("50000")
            ),
        ]
    )
    assert len(entry.lines) == 2


def test_unbalanced_entry_rejected():
    with pytest.raises(ValidationError, match="unbalanced"):
        _entry(
            [
                JournalEntryLine(account_id="cash", debit=Decimal("50000")),
                JournalEntryLine(
                    account_id="contributed_equity", credit=Decimal("49999.99")
                ),
            ]
        )


def test_split_entry_balances_exactly():
    entry = _entry(
        [
            JournalEntryLine(account_id="cash", debit=Decimal("0.10")),
            JournalEntryLine(account_id="a", credit=Decimal("0.05")),
            JournalEntryLine(account_id="b", credit=Decimal("0.05")),
        ]
    )
    assert len(entry.lines) == 3


def test_fewer_than_two_lines_rejected():
    with pytest.raises(ValidationError):
        _entry([JournalEntryLine(account_id="cash", debit=Decimal("1"))])


def test_debit_and_credit_both_positive_rejected():
    with pytest.raises(ValidationError):
        JournalEntryLine(
            account_id="cash", debit=Decimal("1"), credit=Decimal("1")
        )


def test_zero_debit_and_credit_rejected():
    with pytest.raises(ValidationError):
        JournalEntryLine(account_id="cash")


@pytest.mark.parametrize("field", ["debit", "credit"])
def test_negative_amount_rejected(field):
    with pytest.raises(ValidationError):
        JournalEntryLine(account_id="cash", **{field: Decimal("-1")})


def test_journal_amounts_remain_decimal():
    line = JournalEntryLine(account_id="cash", debit="50000")
    assert isinstance(line.debit, Decimal)
    assert isinstance(line.credit, Decimal)
