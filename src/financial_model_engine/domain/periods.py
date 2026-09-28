from pydantic import BaseModel, ConfigDict, Field


class ForecastPeriod(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1)
    index: int = Field(ge=0)
    label: str = Field(min_length=1)
    year: int
    month: int | None = Field(default=None, ge=1, le=12)
