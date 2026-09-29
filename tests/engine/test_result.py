from decimal import Decimal

import pytest
from pydantic import ValidationError

from financial_model_engine.domain import FinancialStatementType, ForecastPeriod
from financial_model_engine.engine import (
    LineItemResult,
    ModelCheck,
    ModelResult,
    PeriodValue,
    StatementResult,
)


def test_valid_period_value():
    pv = PeriodValue(period_id="2027-01", value=Decimal("1000"))
    assert pv.period_id == "2027-01"
    assert pv.value == Decimal("1000")


def test_period_value_preserves_decimal():
    pv = PeriodValue(period_id="2027-01", value="1000.50")
    assert isinstance(pv.value, Decimal)
    assert pv.value == Decimal("1000.50")


def test_valid_line_item_result():
    result = LineItemResult(
        line_item_id="revenue",
        values=[
            PeriodValue(period_id="2027-01", value=Decimal("1000")),
            PeriodValue(period_id="2027-02", value=Decimal("1100")),
        ],
    )
    assert len(result.values) == 2


def test_duplicate_period_id_in_line_item_result_rejected():
    with pytest.raises(ValidationError, match="duplicate period ids"):
        LineItemResult(
            line_item_id="revenue",
            values=[
                PeriodValue(period_id="2027-01", value=Decimal("1000")),
                PeriodValue(period_id="2027-01", value=Decimal("1100")),
            ],
        )


def test_duplicate_line_item_id_in_statement_result_rejected():
    with pytest.raises(ValidationError, match="duplicate line item ids"):
        StatementResult(
            statement_type=FinancialStatementType.INCOME_STATEMENT,
            line_items=[
                LineItemResult(line_item_id="revenue"),
                LineItemResult(line_item_id="revenue"),
            ],
        )


def test_valid_model_check():
    check = ModelCheck(
        id="balance_sheet_balances",
        name="Balance Sheet Balances",
        passed=True,
        difference=Decimal("0"),
    )
    assert check.passed is True
    assert check.message is None


def _period():
    return ForecastPeriod(id="2027-01", index=0, label="Jan 2027", year=2027, month=1)


def _statement(statement_type, line_item_id="x"):
    return StatementResult(
        statement_type=statement_type,
        line_items=[
            LineItemResult(
                line_item_id=line_item_id,
                values=[PeriodValue(period_id="2027-01", value=Decimal("1"))],
            )
        ],
    )


def test_valid_model_result():
    result = ModelResult(
        periods=[_period()],
        operating_schedule=[
            LineItemResult(
                line_item_id="customers",
                values=[PeriodValue(period_id="2027-01", value=Decimal("10"))],
            )
        ],
        income_statement=_statement(FinancialStatementType.INCOME_STATEMENT),
        balance_sheet=_statement(FinancialStatementType.BALANCE_SHEET),
        cash_flow=_statement(FinancialStatementType.CASH_FLOW),
        checks=[ModelCheck(id="c1", name="Check 1", passed=True)],
    )
    assert result.periods[0].id == "2027-01"
    assert result.checks[0].passed is True


def test_duplicate_operating_schedule_ids_rejected():
    with pytest.raises(ValidationError, match="operating_schedule"):
        ModelResult(
            periods=[_period()],
            operating_schedule=[
                LineItemResult(line_item_id="customers"),
                LineItemResult(line_item_id="customers"),
            ],
            income_statement=_statement(FinancialStatementType.INCOME_STATEMENT),
            balance_sheet=_statement(FinancialStatementType.BALANCE_SHEET),
            cash_flow=_statement(FinancialStatementType.CASH_FLOW),
        )
