from collections import Counter
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from financial_model_engine.domain import FinancialStatementType, ForecastPeriod


def _duplicates(ids: list[str]) -> list[str]:
    return sorted(i for i, n in Counter(ids).items() if n > 1)


class PeriodValue(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    period_id: str = Field(min_length=1)
    value: Decimal = Field(allow_inf_nan=False)


class LineItemResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    line_item_id: str = Field(min_length=1)
    values: list[PeriodValue] = Field(default_factory=list)

    @model_validator(mode="after")
    def _unique_period_ids(self) -> "LineItemResult":
        dupes = _duplicates([v.period_id for v in self.values])
        if dupes:
            raise ValueError(
                f"duplicate period ids in line item '{self.line_item_id}': {dupes}"
            )
        return self


class StatementResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    statement_type: FinancialStatementType
    line_items: list[LineItemResult] = Field(default_factory=list)

    @model_validator(mode="after")
    def _unique_line_item_ids(self) -> "StatementResult":
        dupes = _duplicates([li.line_item_id for li in self.line_items])
        if dupes:
            raise ValueError(
                f"duplicate line item ids in {self.statement_type}: {dupes}"
            )
        return self


class ModelCheck(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    passed: bool
    difference: Decimal | None = Field(default=None, allow_inf_nan=False)
    message: str | None = None


class ModelResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    periods: list[ForecastPeriod]
    operating_schedule: list[LineItemResult] = Field(default_factory=list)
    income_statement: StatementResult
    balance_sheet: StatementResult
    cash_flow: StatementResult
    checks: list[ModelCheck] = Field(default_factory=list)

    @model_validator(mode="after")
    def _unique_operating_schedule_ids(self) -> "ModelResult":
        dupes = _duplicates([li.line_item_id for li in self.operating_schedule])
        if dupes:
            raise ValueError(f"duplicate line item ids in operating_schedule: {dupes}")
        return self
