from pydantic import BaseModel, ConfigDict, Field

from financial_model_engine.domain.enums import FinancialStatementType, Unit


class FinancialLineItem(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    statement_type: FinancialStatementType
    unit: Unit
    dependencies: list[str] = Field(default_factory=list)
