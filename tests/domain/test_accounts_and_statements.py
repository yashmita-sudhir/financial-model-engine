import pytest
from pydantic import ValidationError

from financial_model_engine.domain import (
    AccountType,
    FinancialAccount,
    FinancialLineItem,
    FinancialStatementType,
    Unit,
)


def test_valid_financial_account():
    account = FinancialAccount(
        id="cash", name="Cash", account_type=AccountType.ASSET
    )
    assert account.account_type is AccountType.ASSET


def test_invalid_account_type_rejected():
    with pytest.raises(ValidationError):
        FinancialAccount(id="cash", name="Cash", account_type="bogus")


def test_valid_line_item_with_dependencies():
    item = FinancialLineItem(
        id="gross_profit",
        name="Gross Profit",
        statement_type=FinancialStatementType.INCOME_STATEMENT,
        unit=Unit.CURRENCY,
        dependencies=["revenue", "cogs"],
    )
    assert item.dependencies == ["revenue", "cogs"]


def test_line_item_dependencies_default_empty():
    item = FinancialLineItem(
        id="customers",
        name="Customers",
        statement_type=FinancialStatementType.INCOME_STATEMENT,
        unit=Unit.COUNT,
    )
    assert item.dependencies == []


def test_line_item_does_not_validate_dependency_references():
    item = FinancialLineItem(
        id="a",
        name="A",
        statement_type=FinancialStatementType.INCOME_STATEMENT,
        unit=Unit.CURRENCY,
        dependencies=["does_not_exist", "a"],
    )
    assert item.dependencies == ["does_not_exist", "a"]
