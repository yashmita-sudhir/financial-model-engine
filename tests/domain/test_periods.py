import pytest
from pydantic import ValidationError

from financial_model_engine.domain import ForecastPeriod


def test_valid_forecast_period():
    period = ForecastPeriod(
        id="2027-01", index=0, label="Jan 2027", year=2027, month=1
    )
    assert period.id == "2027-01"
    assert period.month == 1


@pytest.mark.parametrize("month", [0, 13, -1])
def test_invalid_month_rejected(month):
    with pytest.raises(ValidationError):
        ForecastPeriod(
            id="p", index=0, label="p", year=2027, month=month
        )


def test_negative_index_rejected():
    with pytest.raises(ValidationError):
        ForecastPeriod(id="p", index=-1, label="p", year=2027, month=1)


def test_month_is_optional():
    period = ForecastPeriod(id="2027", index=0, label="FY2027", year=2027)
    assert period.month is None
