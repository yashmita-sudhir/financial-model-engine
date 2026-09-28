from decimal import Decimal

import pytest
from pydantic import ValidationError

from financial_model_engine.domain import (
    Assumption,
    ModelAssumptions,
    Provenance,
    Unit,
)

VALID = dict(
    starting_customers=Decimal("10"),
    monthly_price=Decimal("100"),
    customer_growth=Decimal("0.15"),
    monthly_marketing=Decimal("5000"),
    monthly_payroll=Decimal("8000"),
    other_opex=Decimal("1000"),
    initial_equity=Decimal("50000"),
    tax_rate=Decimal("0.20"),
    forecast_months=12,
)


def test_valid_assumption():
    a = Assumption(
        id="monthly_growth",
        name="Monthly Customer Growth",
        value=Decimal("0.15"),
        unit=Unit.PERCENTAGE,
        provenance=Provenance.USER,
        confirmed=True,
    )
    assert a.value == Decimal("0.15")
    assert a.source_text is None
    assert a.confirmed is True


def test_assumption_defaults_to_unconfirmed():
    a = Assumption(
        id="x",
        name="X",
        value=Decimal("1"),
        unit=Unit.COUNT,
        provenance=Provenance.SYSTEM_DEFAULT,
    )
    assert a.confirmed is False


def test_valid_model_assumptions():
    m = ModelAssumptions(**VALID)
    assert m.forecast_months == 12
    assert m.tax_rate == Decimal("0.20")


@pytest.mark.parametrize("tax_rate", [Decimal("1.01"), Decimal("-0.01")])
def test_tax_rate_out_of_range_rejected(tax_rate):
    with pytest.raises(ValidationError):
        ModelAssumptions(**{**VALID, "tax_rate": tax_rate})


@pytest.mark.parametrize("tax_rate", [Decimal("0"), Decimal("1")])
def test_tax_rate_bounds_inclusive(tax_rate):
    assert ModelAssumptions(**{**VALID, "tax_rate": tax_rate}).tax_rate == tax_rate


@pytest.mark.parametrize(
    "field", ["monthly_marketing", "monthly_payroll", "other_opex"]
)
def test_negative_expense_rejected(field):
    with pytest.raises(ValidationError):
        ModelAssumptions(**{**VALID, field: Decimal("-1")})


@pytest.mark.parametrize("months", [0, -1, 61])
def test_invalid_forecast_months_rejected(months):
    with pytest.raises(ValidationError):
        ModelAssumptions(**{**VALID, "forecast_months": months})


def test_monthly_price_must_be_positive():
    with pytest.raises(ValidationError):
        ModelAssumptions(**{**VALID, "monthly_price": Decimal("0")})


def test_customer_growth_must_exceed_minus_one():
    with pytest.raises(ValidationError):
        ModelAssumptions(**{**VALID, "customer_growth": Decimal("-1")})
    m = ModelAssumptions(**{**VALID, "customer_growth": Decimal("-0.5")})
    assert m.customer_growth == Decimal("-0.5")


def test_nan_rejected():
    with pytest.raises(ValidationError):
        ModelAssumptions(**{**VALID, "other_opex": Decimal("NaN")})


def test_unknown_field_rejected():
    with pytest.raises(ValidationError):
        ModelAssumptions(**VALID, debt=Decimal("1"))


def test_monetary_values_remain_decimal():
    m = ModelAssumptions(**{**VALID, "monthly_price": "99.99"})
    for name in VALID:
        if name != "forecast_months":
            assert isinstance(getattr(m, name), Decimal), name
    assert m.monthly_price == Decimal("99.99")
