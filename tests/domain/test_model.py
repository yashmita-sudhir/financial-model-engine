from decimal import Decimal

import pytest
from pydantic import ValidationError

from financial_model_engine.domain import (
    AccountType,
    Assumption,
    FinancialAccount,
    FinancialLineItem,
    FinancialModelDefinition,
    FinancialStatementType,
    ForecastPeriod,
    Provenance,
    Unit,
)


def _period(id_="2027-01", index=0):
    return ForecastPeriod(id=id_, index=index, label=id_, year=2027, month=1)


def _assumption(id_):
    return Assumption(
        id=id_,
        name=id_,
        value=Decimal("1"),
        unit=Unit.COUNT,
        provenance=Provenance.USER,
    )


def _account(id_="cash"):
    return FinancialAccount(id=id_, name=id_, account_type=AccountType.ASSET)


def _item(id_="revenue", deps=()):
    return FinancialLineItem(
        id=id_,
        name=id_,
        statement_type=FinancialStatementType.INCOME_STATEMENT,
        unit=Unit.CURRENCY,
        dependencies=list(deps),
    )


def _model(**overrides):
    parts = dict(
        periods=[_period()],
        assumptions=[],
        accounts=[_account()],
        line_items=[_item()],
    )
    parts.update(overrides)
    return FinancialModelDefinition(**parts)


def test_valid_model_definition():
    model = _model()
    assert len(model.line_items) == 1


def test_model_allows_unresolved_dependencies():
    _model(line_items=[_item("revenue", deps=["customers"])])


@pytest.mark.parametrize(
    "field, items",
    [
        ("periods", [_period("p", 0), _period("p", 1)]),
        ("assumptions", [_assumption("g"), _assumption("g")]),
        ("accounts", [_account("cash"), _account("cash")]),
        ("line_items", [_item("revenue"), _item("revenue")]),
    ],
)
def test_duplicate_ids_rejected(field, items):
    with pytest.raises(ValidationError, match="duplicate ids"):
        _model(**{field: items})
