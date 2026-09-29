from financial_model_engine.expressions.nodes import (
    BINARY_NODE_TYPES,
    Constant,
    Expression,
    If,
    PreviousPeriod,
    Reference,
)


def referenced_ids(expression: Expression) -> set[str]:
    """Every stable ID referenced anywhere inside an expression tree.

    A PreviousPeriod("customers") counts as a dependency on "customers".
    """
    ids: set[str] = set()
    _collect(expression, ids)
    return ids


def _collect(expression: Expression, ids: set[str]) -> None:
    if isinstance(expression, (Reference, PreviousPeriod)):
        ids.add(expression.id)
    elif isinstance(expression, Constant):
        pass
    elif isinstance(expression, BINARY_NODE_TYPES):
        _collect(expression.left, ids)
        _collect(expression.right, ids)
    elif isinstance(expression, If):
        _collect(expression.condition, ids)
        _collect(expression.then_expr, ids)
        _collect(expression.else_expr, ids)
    else:
        raise TypeError(f"unknown expression node: {type(expression)!r}")
