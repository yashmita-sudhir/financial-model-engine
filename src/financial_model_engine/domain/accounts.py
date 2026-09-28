from pydantic import BaseModel, ConfigDict, Field

from financial_model_engine.domain.enums import AccountType


class FinancialAccount(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    account_type: AccountType
