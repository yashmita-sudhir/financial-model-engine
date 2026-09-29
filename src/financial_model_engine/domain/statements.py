from pydantic import BaseModel, ConfigDict, Field

from financial_model_engine.domain.enums import FinancialStatementType, Unit
from financial_model_engine.expressions import Expression


class FinancialLineItem(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    statement_type: FinancialStatementType
    unit: Unit
    dependencies: list[str] = Field(default_factory=list)
    formula: Expression | None = None
    initial_formula: Expression | None = None
