from decimal import Decimal

import pytest
from pydantic import ValidationError

from financial_model_engine.expressions import (
    Add,
    Constant,
    Divide,
    Equal,
    ExpressionAdapter,
    GreaterThan,
    If,
    Max,
    Min,
    Multiply,
    PreviousPeriod,
    Reference,
    Subtract,
)


def test_reference_creation():
    ref = Reference(id="monthly_price")
    assert ref.id == "monthly_price"
    assert ref.kind == "reference"


def test_empty_reference_rejected():
    with pytest.raises(ValidationError):
        Reference(id="")


def test_constant_uses_decimal():
    const = Constant(value=Decimal("0"))
    assert isinstance(const.value, Decimal)
    const2 = Constant(value="1150.50")
    assert const2.value == Decimal("1150.50")


def test_constant_rejects_nan():
    with pytest.raises(ValidationError):
        Constant(value=Decimal("NaN"))


def test_add_expression():
    expr = Add(left=Reference(id="a"), right=Reference(id="b"))
    assert expr.left.id == "a"
    assert expr.right.id == "b"


def test_subtract_expression():
    expr = Subtract(left=Reference(id="revenue"), right=Reference(id="cogs"))
    assert expr.kind == "subtract"


def test_multiply_expression():
    expr = Multiply(left=Reference(id="customers"), right=Reference(id="monthly_price"))
    assert expr.kind == "multiply"


def test_divide_expression():
    expr = Divide(left=Reference(id="net_income"), right=Reference(id="revenue"))
    assert expr.kind == "divide"


def test_min_expression():
    expr = Min(left=Constant(value=Decimal("0")), right=Reference(id="x"))
    assert expr.kind == "min"


def test_max_expression():
    expr = Max(
        left=Constant(value=Decimal("0")),
        right=Multiply(left=Reference(id="pretax_income"), right=Reference(id="tax_rate")),
    )
    assert expr.kind == "max"


def test_comparison_expression():
    cmp = GreaterThan(left=Reference(id="pretax_income"), right=Constant(value=Decimal("0")))
    assert cmp.kind == "greater_than"


def test_comparison_requires_valid_operands():
    with pytest.raises(ValidationError):
        GreaterThan(left="not an expression", right=Constant(value=Decimal("0")))


def test_if_expression():
    expr = If(
        condition=Equal(left=Reference(id="tax_rate"), right=Constant(value=Decimal("0"))),
        then_expr=Constant(value=Decimal("0")),
        else_expr=Reference(id="tax"),
    )
    assert expr.condition.kind == "equal"
    assert expr.then_expr.value == Decimal("0")


def test_previous_period_expression():
    expr = PreviousPeriod(id="customers")
    assert expr.id == "customers"
    assert expr.kind == "previous_period"


def test_previous_period_rejects_empty_id():
    with pytest.raises(ValidationError):
        PreviousPeriod(id="")


def test_nested_expression_serialization_round_trip():
    expr = Max(
        left=Constant(value=Decimal("0")),
        right=Multiply(left=Reference(id="pretax_income"), right=Reference(id="tax_rate")),
    )
    dumped = expr.model_dump()
    restored = ExpressionAdapter.validate_python(dumped)
    assert restored == expr

    dumped_json = expr.model_dump_json()
    restored_from_json = ExpressionAdapter.validate_json(dumped_json)
    assert restored_from_json == expr


def test_expression_is_immutable():
    expr = Add(left=Reference(id="a"), right=Reference(id="b"))
    with pytest.raises(ValidationError):
        expr.kind = "subtract"
