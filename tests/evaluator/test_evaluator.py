from decimal import Decimal

import pytest

from financial_model_engine.evaluator import (
    DivisionByZeroError,
    EvaluationContext,
    MissingPreviousPeriodValueError,
    MissingValueError,
    evaluate,
)
from financial_model_engine.expressions import (
    Add,
    Constant,
    Divide,
    Equal,
    GreaterThan,
    GreaterThanOrEqual,
    If,
    LessThan,
    LessThanOrEqual,
    Max,
    Min,
    Multiply,
    PreviousPeriod,
    Reference,
    Subtract,
)


def ctx(current=None, previous=None) -> EvaluationContext:
    return EvaluationContext(current_values=current or {}, previous_values=previous or {})


def test_reference_lookup():
    result = evaluate(Reference(id="monthly_price"), ctx({"monthly_price": Decimal("100")}))
    assert result == Decimal("100")


def test_missing_reference_raises():
    with pytest.raises(MissingValueError) as exc_info:
        evaluate(Reference(id="monthly_price"), ctx())
    assert exc_info.value.stable_id == "monthly_price"


def test_constant_evaluation():
    assert evaluate(Constant(value=Decimal("10")), ctx()) == Decimal("10")


def test_add():
    result = evaluate(
        Add(left=Constant(value=Decimal("2")), right=Constant(value=Decimal("3"))), ctx()
    )
    assert result == Decimal("5")


def test_subtract():
    result = evaluate(
        Subtract(left=Constant(value=Decimal("5")), right=Constant(value=Decimal("3"))), ctx()
    )
    assert result == Decimal("2")


def test_multiply():
    result = evaluate(
        Multiply(left=Reference(id="customers"), right=Reference(id="monthly_price")),
        ctx({"customers": Decimal("10"), "monthly_price": Decimal("100")}),
    )
    assert result == Decimal("1000")


def test_divide():
    result = evaluate(
        Divide(left=Constant(value=Decimal("10")), right=Constant(value=Decimal("4"))), ctx()
    )
    assert result == Decimal("2.5")


def test_divide_by_zero_raises():
    with pytest.raises(DivisionByZeroError):
        evaluate(
            Divide(left=Constant(value=Decimal("10")), right=Constant(value=Decimal("0"))),
            ctx(),
        )


def test_min():
    result = evaluate(
        Min(left=Constant(value=Decimal("5")), right=Constant(value=Decimal("2"))), ctx()
    )
    assert result == Decimal("2")


def test_max():
    result = evaluate(
        Max(left=Constant(value=Decimal("0")), right=Constant(value=Decimal("-5"))), ctx()
    )
    assert result == Decimal("0")


@pytest.mark.parametrize(
    "node_cls, left, right, expected",
    [
        (GreaterThan, "5", "3", True),
        (GreaterThan, "3", "5", False),
        (GreaterThanOrEqual, "5", "5", True),
        (GreaterThanOrEqual, "4", "5", False),
        (LessThan, "3", "5", True),
        (LessThan, "5", "3", False),
        (LessThanOrEqual, "5", "5", True),
        (LessThanOrEqual, "6", "5", False),
        (Equal, "5", "5", True),
        (Equal, "5", "6", False),
    ],
)
def test_comparisons(node_cls, left, right, expected):
    node = node_cls(left=Constant(value=Decimal(left)), right=Constant(value=Decimal(right)))
    assert evaluate(node, ctx()) is expected


def test_if_true_branch():
    expr = If(
        condition=GreaterThan(left=Reference(id="pretax_income"), right=Constant(value=Decimal("0"))),
        then_expr=Multiply(left=Reference(id="pretax_income"), right=Reference(id="tax_rate")),
        else_expr=Constant(value=Decimal("0")),
    )
    result = evaluate(expr, ctx({"pretax_income": Decimal("1000"), "tax_rate": Decimal("0.20")}))
    assert result == Decimal("200.00")


def test_if_false_branch():
    expr = If(
        condition=GreaterThan(left=Reference(id="pretax_income"), right=Constant(value=Decimal("0"))),
        then_expr=Multiply(left=Reference(id="pretax_income"), right=Reference(id="tax_rate")),
        else_expr=Constant(value=Decimal("0")),
    )
    result = evaluate(expr, ctx({"pretax_income": Decimal("-1000"), "tax_rate": Decimal("0.20")}))
    assert result == Decimal("0")


def test_if_evaluates_lazily():
    """The untaken branch must never be evaluated: it references an ID that
    doesn't exist in the context, which would raise if evaluated."""
    expr = If(
        condition=GreaterThan(left=Reference(id="pretax_income"), right=Constant(value=Decimal("0"))),
        then_expr=Constant(value=Decimal("1")),
        else_expr=Divide(left=Constant(value=Decimal("1")), right=Reference(id="does_not_exist")),
    )
    result = evaluate(expr, ctx({"pretax_income": Decimal("1000")}))
    assert result == Decimal("1")

    expr_reversed = If(
        condition=GreaterThan(left=Reference(id="pretax_income"), right=Constant(value=Decimal("0"))),
        then_expr=Divide(left=Constant(value=Decimal("1")), right=Reference(id="does_not_exist")),
        else_expr=Constant(value=Decimal("1")),
    )
    result_reversed = evaluate(expr_reversed, ctx({"pretax_income": Decimal("-1000")}))
    assert result_reversed == Decimal("1")


def test_previous_period_success():
    result = evaluate(PreviousPeriod(id="customers"), ctx(previous={"customers": Decimal("9")}))
    assert result == Decimal("9")


def test_previous_period_missing_raises():
    with pytest.raises(MissingPreviousPeriodValueError) as exc_info:
        evaluate(PreviousPeriod(id="customers"), ctx())
    assert exc_info.value.stable_id == "customers"


def test_previous_period_does_not_fall_back_to_current():
    with pytest.raises(MissingPreviousPeriodValueError):
        evaluate(PreviousPeriod(id="customers"), ctx(current={"customers": Decimal("10")}))


def test_nested_revenue_expression():
    expr = Multiply(left=Reference(id="customers"), right=Reference(id="monthly_price"))
    result = evaluate(expr, ctx({"customers": Decimal("10"), "monthly_price": Decimal("100")}))
    assert result == Decimal("1000")


def test_nested_tax_expression():
    expr = Max(
        left=Constant(value=Decimal("0")),
        right=Multiply(left=Reference(id="pretax_income"), right=Reference(id="tax_rate")),
    )
    assert evaluate(
        expr, ctx({"pretax_income": Decimal("1000"), "tax_rate": Decimal("0.20")})
    ) == Decimal("200.00")
    assert evaluate(
        expr, ctx({"pretax_income": Decimal("-1000"), "tax_rate": Decimal("0.20")})
    ) == Decimal("0")


def test_customer_growth_expression_with_previous_period():
    expr = Multiply(
        left=PreviousPeriod(id="customers"),
        right=Add(left=Constant(value=Decimal("1")), right=Reference(id="customer_growth")),
    )
    result = evaluate(
        expr,
        ctx(current={"customer_growth": Decimal("0.15")}, previous={"customers": Decimal("10")}),
    )
    assert result == Decimal("11.50")


def test_decimal_precision_preserved():
    expr = Add(left=Constant(value=Decimal("0.1")), right=Constant(value=Decimal("0.2")))
    assert evaluate(expr, ctx()) == Decimal("0.3")


def test_expression_not_mutated_by_evaluation():
    expr = Multiply(left=Reference(id="customers"), right=Reference(id="monthly_price"))
    before = expr.model_dump()
    evaluate(expr, ctx({"customers": Decimal("10"), "monthly_price": Decimal("100")}))
    assert expr.model_dump() == before
