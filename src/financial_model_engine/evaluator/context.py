from dataclasses import dataclass, field
from decimal import Decimal

from financial_model_engine.evaluator.errors import (
    MissingPreviousPeriodValueError,
    MissingValueError,
)


@dataclass(frozen=True)
class EvaluationContext:
    """Values a single expression evaluation can see.

    `current_values` is this period's assumptions and already-calculated
    line items. `previous_values` is the prior period's line-item values.
    The two are looked up separately and never fall back to each other.
    """

    current_values: dict[str, Decimal] = field(default_factory=dict)
    previous_values: dict[str, Decimal] = field(default_factory=dict)

    def get_current(self, stable_id: str) -> Decimal:
        try:
            return self.current_values[stable_id]
        except KeyError:
            raise MissingValueError(stable_id) from None

    def get_previous(self, stable_id: str) -> Decimal:
        try:
            return self.previous_values[stable_id]
        except KeyError:
            raise MissingPreviousPeriodValueError(stable_id) from None
