from decimal import Decimal

import pytest

from financial_model_engine.domain import (
    FinancialLineItem,
    FinancialStatementType,
    ForecastPeriod,
    ModelAssumptions,
    Unit,
)
from financial_model_engine.expressions import Add, Constant, Multiply, PreviousPeriod, Reference
from financial_model_engine.forecasting import MissingFormulaError, run_forecast
from financial_model_engine.forecasting.result import ForecastResult


def make_assumptions(**overrides) -> ModelAssumptions:
    base = dict(
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
    base.update(overrides)
    return ModelAssumptions(**base)


def make_periods(labels: list[str]) -> list[ForecastPeriod]:
    return [
        ForecastPeriod(id=label, index=i, label=label, year=2027, month=i + 1)
        for i, label in enumerate(labels)
    ]


def customers_line_item() -> FinancialLineItem:
    return FinancialLineItem(
        id="customers",
        name="Customers",
        statement_type=FinancialStatementType.INCOME_STATEMENT,
        unit=Unit.COUNT,
        dependencies=["starting_customers", "customer_growth"],
        initial_formula=Reference(id="starting_customers"),
        formula=Multiply(
            left=PreviousPeriod(id="customers"),
            right=Add(left=Constant(value=Decimal("1")), right=Reference(id="customer_growth")),
        ),
    )


def revenue_line_item() -> FinancialLineItem:
    return FinancialLineItem(
        id="revenue",
        name="Revenue",
        statement_type=FinancialStatementType.INCOME_STATEMENT,
        unit=Unit.CURRENCY,
        dependencies=["customers", "monthly_price"],
        formula=Multiply(left=Reference(id="customers"), right=Reference(id="monthly_price")),
    )


def values_by_period(result: ForecastResult, line_item_id: str) -> dict[str, Decimal]:
    for li in result.line_items:
        if li.line_item_id == line_item_id:
            return {pv.period_id: pv.value for pv in li.values}
    raise KeyError(line_item_id)


def test_one_period_forecast():
    result = run_forecast(make_assumptions(), make_periods(["Jan"]), [customers_line_item()])
    assert values_by_period(result, "customers") == {"Jan": Decimal("10")}


def test_multiple_period_forecast():
    result = run_forecast(
        make_assumptions(),
        make_periods(["Jan", "Feb", "Mar"]),
        [customers_line_item()],
    )
    values = values_by_period(result, "customers")
    assert list(values.keys()) == ["Jan", "Feb", "Mar"]


def test_assumption_reference_evaluation():
    item = FinancialLineItem(
        id="price_echo",
        name="Price Echo",
        statement_type=FinancialStatementType.INCOME_STATEMENT,
        unit=Unit.CURRENCY,
        dependencies=["monthly_price"],
        formula=Reference(id="monthly_price"),
    )
    result = run_forecast(make_assumptions(), make_periods(["Jan"]), [item])
    assert values_by_period(result, "price_echo")["Jan"] == Decimal("100")


def test_line_item_to_line_item_dependency():
    result = run_forecast(
        make_assumptions(),
        make_periods(["Jan"]),
        [customers_line_item(), revenue_line_item()],
    )
    assert values_by_period(result, "revenue")["Jan"] == Decimal("1000")


def test_calculation_order_is_used_regardless_of_input_order():
    # revenue is listed before customers; the engine must still resolve
    # customers first because revenue depends on it.
    result = run_forecast(
        make_assumptions(),
        make_periods(["Jan"]),
        [revenue_line_item(), customers_line_item()],
    )
    assert values_by_period(result, "revenue")["Jan"] == Decimal("1000")
    assert [li.line_item_id for li in result.line_items] == ["customers", "revenue"]


def test_first_period_uses_initial_formula():
    result = run_forecast(make_assumptions(), make_periods(["Jan"]), [customers_line_item()])
    assert values_by_period(result, "customers")["Jan"] == Decimal("10")


def test_later_periods_use_recurring_formula():
    result = run_forecast(
        make_assumptions(), make_periods(["Jan", "Feb"]), [customers_line_item()]
    )
    values = values_by_period(result, "customers")
    assert values["Jan"] == Decimal("10")
    assert values["Feb"] == Decimal("11.50")


def test_previous_period_works_across_periods():
    result = run_forecast(
        make_assumptions(), make_periods(["Jan", "Feb", "Mar"]), [customers_line_item()]
    )
    values = values_by_period(result, "customers")
    assert values["Jan"] == Decimal("10")
    assert values["Feb"] == Decimal("11.50")
    assert values["Mar"] == Decimal("13.225")


def test_customers_growth_sequence_exact():
    result = run_forecast(
        make_assumptions(), make_periods(["Jan", "Feb", "Mar"]), [customers_line_item()]
    )
    values = values_by_period(result, "customers")
    assert values["Jan"] == Decimal("10")
    assert values["Feb"] == Decimal("11.50")
    assert values["Mar"] == Decimal("13.225")


def test_revenue_follows_customers_times_price():
    result = run_forecast(
        make_assumptions(),
        make_periods(["Jan", "Feb", "Mar"]),
        [customers_line_item(), revenue_line_item()],
    )
    revenue = values_by_period(result, "revenue")
    assert revenue["Jan"] == Decimal("1000")
    assert revenue["Feb"] == Decimal("1150.00")
    assert revenue["Mar"] == Decimal("1322.500")


def test_missing_formula_raises():
    item = FinancialLineItem(
        id="orphan",
        name="Orphan",
        statement_type=FinancialStatementType.INCOME_STATEMENT,
        unit=Unit.CURRENCY,
    )
    with pytest.raises(MissingFormulaError) as exc_info:
        run_forecast(make_assumptions(), make_periods(["Jan"]), [item])
    assert exc_info.value.line_item_id == "orphan"
    assert exc_info.value.period_id == "Jan"


def test_missing_initial_value_error_surfaces():
    # formula-only line item (no initial_formula) needs PreviousPeriod in
    # period 1, where no prior value exists — the evaluator's error must
    # propagate unchanged, not be swallowed or replaced with a default.
    from financial_model_engine.evaluator import MissingPreviousPeriodValueError

    item = FinancialLineItem(
        id="customers",
        name="Customers",
        statement_type=FinancialStatementType.INCOME_STATEMENT,
        unit=Unit.COUNT,
        formula=Multiply(
            left=PreviousPeriod(id="customers"),
            right=Add(left=Constant(value=Decimal("1")), right=Reference(id="customer_growth")),
        ),
    )
    with pytest.raises(MissingPreviousPeriodValueError) as exc_info:
        run_forecast(make_assumptions(), make_periods(["Jan"]), [item])
    assert exc_info.value.stable_id == "customers"


def test_decimal_precision_preserved():
    result = run_forecast(
        make_assumptions(),
        make_periods(["Jan", "Feb", "Mar"]),
        [customers_line_item()],
    )
    values = values_by_period(result, "customers")
    assert values["Mar"] == Decimal("13.225")
    assert isinstance(values["Mar"], Decimal)


def test_assumptions_not_mutated():
    assumptions = make_assumptions()
    before = assumptions.model_dump()
    run_forecast(
        assumptions,
        make_periods(["Jan", "Feb"]),
        [customers_line_item(), revenue_line_item()],
    )
    assert assumptions.model_dump() == before


def test_line_items_not_mutated():
    customers = customers_line_item()
    revenue = revenue_line_item()
    before_customers = customers.model_dump()
    before_revenue = revenue.model_dump()
    run_forecast(make_assumptions(), make_periods(["Jan", "Feb"]), [customers, revenue])
    assert customers.model_dump() == before_customers
    assert revenue.model_dump() == before_revenue


def test_period_order_preserved_in_result():
    periods = make_periods(["Jan", "Feb", "Mar"])
    result = run_forecast(make_assumptions(), periods, [customers_line_item()])
    assert [p.id for p in result.periods] == ["Jan", "Feb", "Mar"]


def test_forecast_result_contains_correct_period_value_entries():
    result = run_forecast(
        make_assumptions(), make_periods(["Jan", "Feb"]), [customers_line_item()]
    )
    customers_result = next(li for li in result.line_items if li.line_item_id == "customers")
    assert [pv.period_id for pv in customers_result.values] == ["Jan", "Feb"]
    assert customers_result.values[0].value == Decimal("10")
    assert customers_result.values[1].value == Decimal("11.50")
