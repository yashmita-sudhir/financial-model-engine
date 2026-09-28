from enum import StrEnum


class Unit(StrEnum):
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    COUNT = "count"
    DAYS = "days"
    RATIO = "ratio"


class Provenance(StrEnum):
    USER = "user"
    SYSTEM_DEFAULT = "system_default"
    DERIVED = "derived"


class FinancialStatementType(StrEnum):
    INCOME_STATEMENT = "income_statement"
    BALANCE_SHEET = "balance_sheet"
    CASH_FLOW = "cash_flow"


class AccountType(StrEnum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"
