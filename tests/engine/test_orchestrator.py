from decimal import Decimal

import pytest

from financial_model_engine.domain import (
    FinancialLineItem,
    FinancialModelDefinition,
    FinancialStatementType,
    ModelAssumptions,
    Unit,
)
from financial_model_engine.engine import (
    LineItemResult,
    ModelCheck,
    ModelIntegrityError,
    ModelResult,
    PeriodValue,
    StatementResult,
    run_model,
)
from financial_model_engine.engine.orchestrator import run_model as run_model_direct


def item(id_, deps=()):
    return FinancialLineItem(
        id=id_,
        name=id_,
        statement_type=FinancialStatementType.INCOME_STATEMENT,
        unit=Unit.CURRENCY,
        dependencies=list(deps),
    )


def make_model_definition():
    return FinancialModelDefinition(
        periods=[],
        assumptions=[],
        accounts=[],
        line_items=[
            item("customers", ["starting_customers", "customer_growth"]),
            item("revenue", ["customers", "monthly_price"]),
        ],
    )


def make_assumptions():
    return ModelAssumptions(
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


def empty_statement(statement_type):
    return StatementResult(statement_type=statement_type, line_items=[])


def make_result(checks):
    return ModelResult(
        periods=[],
        operating_schedule=[],
        income_statement=empty_statement(FinancialStatementType.INCOME_STATEMENT),
        balance_sheet=empty_statement(FinancialStatementType.BALANCE_SHEET),
        cash_flow=empty_statement(FinancialStatementType.CASH_FLOW),
        checks=checks,
    )


class FakeFinanceEngine:
    def __init__(self, checks=()):
        self.checks = list(checks)
        self.received_assumptions = None
        self.received_order = None

    def run(self, assumptions, calculation_order):
        self.received_assumptions = assumptions
        self.received_order = calculation_order
        return make_result(self.checks)


def test_fake_engine_satisfies_finance_engine_protocol():
    engine = FakeFinanceEngine()
    assumptions = make_assumptions()
    result = engine.run(assumptions, ["customers", "revenue"])
    assert isinstance(result, ModelResult)


def test_orchestrator_builds_graph_and_obtains_calculation_order():
    engine = FakeFinanceEngine()
    run_model(make_assumptions(), make_model_definition(), engine)
    assert engine.received_order == ["customers", "revenue"]


def test_orchestrator_calls_finance_engine_with_assumptions():
    engine = FakeFinanceEngine()
    assumptions = make_assumptions()
    run_model(assumptions, make_model_definition(), engine)
    assert engine.received_assumptions is assumptions


def test_orchestrator_returns_model_result_when_checks_pass():
    engine = FakeFinanceEngine(
        checks=[ModelCheck(id="c1", name="Check 1", passed=True)]
    )
    result = run_model(make_assumptions(), make_model_definition(), engine)
    assert isinstance(result, ModelResult)
    assert result.checks[0].passed is True


def test_orchestrator_raises_on_failed_check():
    engine = FakeFinanceEngine(
        checks=[
            ModelCheck(id="c1", name="Check 1", passed=True),
            ModelCheck(id="c2", name="Check 2", passed=False, message="off by 1"),
        ]
    )
    with pytest.raises(ModelIntegrityError) as exc_info:
        run_model(make_assumptions(), make_model_definition(), engine)
    assert exc_info.value.failed_check_ids == ["c2"]


def test_engine_receives_only_line_item_order_not_full_graph_order():
    engine = FakeFinanceEngine()
    run_model(make_assumptions(), make_model_definition(), engine)
    # assumption ids must never appear in what the finance engine receives
    assert "starting_customers" not in engine.received_order
    assert "monthly_price" not in engine.received_order
    assert set(engine.received_order) == {"customers", "revenue"}


def test_orchestrator_importable_directly_from_module():
    engine = FakeFinanceEngine()
    result = run_model_direct(make_assumptions(), make_model_definition(), engine)
    assert isinstance(result, ModelResult)
