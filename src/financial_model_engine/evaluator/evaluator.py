import operator
from decimal import Decimal

from financial_model_engine.evaluator.context import EvaluationContext
from financial_model_engine.evaluator.errors import (
    DivisionByZeroError,
    UnsupportedExpressionError,
)
from financial_model_engine.expressions import (
    Add,
    Constant,
    Divide,
    Equal,
    Expression,
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

_ARITHMETIC_OPS = {
    Add: operator.add,
    Subtract: operator.sub,
    Multiply: operator.mul,
}

_COMPARISON_OPS = {
    GreaterThan: operator.gt,
    GreaterThanOrEqual: operator.ge,
    LessThan: operator.lt,
    LessThanOrEqual: operator.le,
    Equal: operator.eq,
}


def evaluate(expression: Expression, context: EvaluationContext) -> Decimal | bool:
    """Evaluate an expression tree to a Decimal or bool. Never uses eval()."""
    node_type = type(expression)

    if node_type is Reference:
        return context.get_current(expression.id)

    if node_type is Constant:
        return expression.value

    if node_type is PreviousPeriod:
        return context.get_previous(expression.id)

    if node_type is Divide:
        left = evaluate(expression.left, context)
        right = evaluate(expression.right, context)
        if right == 0:
            raise DivisionByZeroError()
        return left / right

    if node_type in _ARITHMETIC_OPS:
        left = evaluate(expression.left, context)
        right = evaluate(expression.right, context)
        return _ARITHMETIC_OPS[node_type](left, right)

    if node_type is Min:
        return min(evaluate(expression.left, context), evaluate(expression.right, context))

    if node_type is Max:
        return max(evaluate(expression.left, context), evaluate(expression.right, context))

    if node_type in _COMPARISON_OPS:
        left = evaluate(expression.left, context)
        right = evaluate(expression.right, context)
        return _COMPARISON_OPS[node_type](left, right)

    if node_type is If:
        if evaluate(expression.condition, context):
            return evaluate(expression.then_expr, context)
        return evaluate(expression.else_expr, context)

    raise UnsupportedExpressionError(expression)
