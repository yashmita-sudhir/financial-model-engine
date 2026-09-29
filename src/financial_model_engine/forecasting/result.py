from collections import Counter

from pydantic import BaseModel, ConfigDict, Field, model_validator

from financial_model_engine.domain import ForecastPeriod
from financial_model_engine.engine import LineItemResult


class ForecastResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    periods: list[ForecastPeriod]
    line_items: list[LineItemResult] = Field(default_factory=list)

    @model_validator(mode="after")
    def _unique_line_item_ids(self) -> "ForecastResult":
        counts = Counter(li.line_item_id for li in self.line_items)
        dupes = sorted(i for i, n in counts.items() if n > 1)
        if dupes:
            raise ValueError(f"duplicate line item ids in forecast result: {dupes}")
        return self
