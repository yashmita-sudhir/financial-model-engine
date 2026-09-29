"""A minimal, structured financial-expression AST.

Every node is an immutable, serializable Pydantic model. There are no raw
formula strings and no eval(): a Python evaluator and an Excel formula
compiler will later walk the same tree and each decide, node by node, what
"Multiply" means in their own domain.

Node classes reference each other recursively (e.g. Add.left: Expression),
so `from __future__ import annotations` defers evaluating annotations until
`model_rebuild()` is called at the bottom of this file, once every class and
the Expression/Comparison unions exist in this module's namespace.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class _Node(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


# --- leaves -----------------------------------------------------------------


class Reference(_Node):
    """A reference to another assumption or line item, by stable ID."""

    kind: Literal["reference"] = "reference"
    id: str = Field(min_length=1)


class Constant(_Node):
    """A fixed numeric value."""

    kind: Literal["constant"] = "constant"
    value: Decimal = Field(allow_inf_nan=False)


class PreviousPeriod(_Node):
    """A reference to a line item's value from the prior forecast period.

    Represented only — not evaluated and not compiled to Excel here.
    """

    kind: Literal["previous_period"] = "previous_period"
    id: str = Field(min_length=1)


# --- arithmetic ---------------------------------------------------------------


class Add(_Node):
    kind: Literal["add"] = "add"
    left: Expression
    right: Expression


class Subtract(_Node):
    kind: Literal["subtract"] = "subtract"
    left: Expression
    right: Expression


class Multiply(_Node):
    kind: Literal["multiply"] = "multiply"
    left: Expression
    right: Expression


class Divide(_Node):
    kind: Literal["divide"] = "divide"
    left: Expression
    right: Expression


class Min(_Node):
    kind: Literal["min"] = "min"
    left: Expression
    right: Expression


class Max(_Node):
    kind: Literal["max"] = "max"
    left: Expression
    right: Expression


# --- comparisons (only valid as an If condition, not general expressions) ---


class GreaterThan(_Node):
    kind: Literal["greater_than"] = "greater_than"
    left: Expression
    right: Expression


class GreaterThanOrEqual(_Node):
    kind: Literal["greater_than_or_equal"] = "greater_than_or_equal"
    left: Expression
    right: Expression


class LessThan(_Node):
    kind: Literal["less_than"] = "less_than"
    left: Expression
    right: Expression


class LessThanOrEqual(_Node):
    kind: Literal["less_than_or_equal"] = "less_than_or_equal"
    left: Expression
    right: Expression


class Equal(_Node):
    kind: Literal["equal"] = "equal"
    left: Expression
    right: Expression


Comparison = Annotated[
    Union[GreaterThan, GreaterThanOrEqual, LessThan, LessThanOrEqual, Equal],
    Field(discriminator="kind"),
]


class If(_Node):
    kind: Literal["if"] = "if"
    condition: Comparison
    then_expr: Expression
    else_expr: Expression


Expression = Annotated[
    Union[
        Reference,
        Constant,
        PreviousPeriod,
        Add,
        Subtract,
        Multiply,
        Divide,
        Min,
        Max,
        If,
    ],
    Field(discriminator="kind"),
]

BINARY_NODE_TYPES = (
    Add,
    Subtract,
    Multiply,
    Divide,
    Min,
    Max,
    GreaterThan,
    GreaterThanOrEqual,
    LessThan,
    LessThanOrEqual,
    Equal,
)

for _cls in (*BINARY_NODE_TYPES, If):
    _cls.model_rebuild()

ExpressionAdapter: TypeAdapter[Expression] = TypeAdapter(Expression)
