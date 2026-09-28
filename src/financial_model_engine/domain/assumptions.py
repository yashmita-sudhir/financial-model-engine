from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from financial_model_engine.domain.enums import Provenance, Unit


class Assumption(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    value: Decimal = Field(allow_inf_nan=False)
    unit: Unit
    provenance: Provenance
    source_text: str | None = None
    confirmed: bool = False


class ModelAssumptions(BaseModel):
    """V1 contract between the system layer and the calculation engine.

    Percentages are fractions: 0.15 means 15%.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    starting_customers: Decimal = Field(ge=0, allow_inf_nan=False)
    monthly_price: Decimal = Field(gt=0, allow_inf_nan=False)
    customer_growth: Decimal = Field(gt=-1, allow_inf_nan=False)
    monthly_marketing: Decimal = Field(ge=0, allow_inf_nan=False)
    monthly_payroll: Decimal = Field(ge=0, allow_inf_nan=False)
    other_opex: Decimal = Field(ge=0, allow_inf_nan=False)
    initial_equity: Decimal = Field(ge=0, allow_inf_nan=False)
    tax_rate: Decimal = Field(ge=0, le=1, allow_inf_nan=False)
    forecast_months: int = Field(ge=1, le=60)
