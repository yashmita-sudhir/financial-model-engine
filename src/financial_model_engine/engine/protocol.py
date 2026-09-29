from typing import Protocol

from financial_model_engine.domain import ModelAssumptions
from financial_model_engine.engine.result import ModelResult


class FinanceEngine(Protocol):
    """The interface Person 2's calculation engine must implement.

    It receives only the assumptions and the line-item calculation order —
    never the dependency graph or the model definition. Ordering and
    dependency resolution are already handled before this is called.
    """

    def run(
        self,
        assumptions: ModelAssumptions,
        calculation_order: list[str],
    ) -> ModelResult: ...
