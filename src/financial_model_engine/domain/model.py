from collections import Counter
from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, model_validator

from financial_model_engine.domain.accounts import FinancialAccount
from financial_model_engine.domain.assumptions import Assumption
from financial_model_engine.domain.periods import ForecastPeriod
from financial_model_engine.domain.statements import FinancialLineItem


def _duplicates(ids: Iterable[str]) -> list[str]:
    return sorted(i for i, n in Counter(ids).items() if n > 1)


class FinancialModelDefinition(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    periods: list[ForecastPeriod]
    assumptions: list[Assumption]
    accounts: list[FinancialAccount]
    line_items: list[FinancialLineItem]

    @model_validator(mode="after")
    def _unique_ids(self) -> "FinancialModelDefinition":
        for name in ("periods", "assumptions", "accounts", "line_items"):
            dupes = _duplicates(item.id for item in getattr(self, name))
            if dupes:
                raise ValueError(f"duplicate ids in {name}: {dupes}")
        return self
