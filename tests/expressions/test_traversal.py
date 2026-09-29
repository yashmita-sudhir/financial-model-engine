from decimal import Decimal

from financial_model_engine.expressions import (
    Constant,
    Equal,
    If,
    Max,
    Multiply,
    PreviousPeriod,
    Reference,
    referenced_ids,
)


def test_referenced_ids_simple_expression():
    expr = Multiply(left=Reference(id="customers"), right=Reference(id="monthly_price"))
    assert referenced_ids(expr) == {"customers", "monthly_price"}


def test_referenced_ids_nested_expression():
    expr = Max(
        left=Constant(value=Decimal("0")),
        right=Multiply(left=Reference(id="pretax_income"), right=Reference(id="tax_rate")),
    )
    assert referenced_ids(expr) == {"pretax_income", "tax_rate"}


def test_referenced_ids_previous_period_counts_as_dependency():
    expr = PreviousPeriod(id="customers")
    assert referenced_ids(expr) == {"customers"}


def test_referenced_ids_constant_only_expression():
    assert referenced_ids(Constant(value=Decimal("0"))) == set()


def test_referenced_ids_if_expression_includes_condition():
    expr = If(
        condition=Equal(left=Reference(id="tax_rate"), right=Constant(value=Decimal("0"))),
        then_expr=Constant(value=Decimal("0")),
        else_expr=Reference(id="tax"),
    )
    assert referenced_ids(expr) == {"tax_rate", "tax"}


def test_repeated_references_deduplicate():
    expr = Multiply(left=Reference(id="x"), right=Reference(id="x"))
    assert referenced_ids(expr) == {"x"}
