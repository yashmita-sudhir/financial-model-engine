class ForecastError(Exception):
    """Base class for forecast-orchestration errors."""


class MissingFormulaError(ForecastError):
    def __init__(self, line_item_id: str, period_id: str):
        self.line_item_id = line_item_id
        self.period_id = period_id
        super().__init__(
            f"line item '{line_item_id}' has no usable formula for period '{period_id}'"
        )
