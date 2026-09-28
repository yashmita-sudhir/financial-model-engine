from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class JournalEntryLine(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    account_id: str = Field(min_length=1)
    debit: Decimal = Field(default=Decimal("0"), ge=0, allow_inf_nan=False)
    credit: Decimal = Field(default=Decimal("0"), ge=0, allow_inf_nan=False)

    @model_validator(mode="after")
    def _exactly_one_side(self) -> "JournalEntryLine":
        if self.debit > 0 and self.credit > 0:
            raise ValueError("a line cannot have both a debit and a credit")
        if self.debit == 0 and self.credit == 0:
            raise ValueError("a line must have a positive debit or credit")
        return self


class JournalEntry(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1)
    description: str
    period_id: str = Field(min_length=1)
    lines: list[JournalEntryLine] = Field(min_length=2)

    @model_validator(mode="after")
    def _balanced(self) -> "JournalEntry":
        debits = sum((line.debit for line in self.lines), Decimal("0"))
        credits = sum((line.credit for line in self.lines), Decimal("0"))
        if debits != credits:
            raise ValueError(
                f"unbalanced entry: debits {debits} != credits {credits}"
            )
        return self
