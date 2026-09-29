from decimal import Decimal

from financial_model_engine.domain import (
    FinancialLineItem,
    ForecastPeriod,
    ModelAssumptions,
)
from financial_model_engine.engine import LineItemResult, PeriodValue
from financial_model_engine.evaluator import EvaluationContext, evaluate
from financial_model_engine.forecasting.errors import MissingFormulaError
from financial_model_engine.forecasting.result import ForecastResult
from financial_model_engine.graph import build_graph, calculation_order


def _assumption_values(assumptions: ModelAssumptions) -> dict[str, Decimal]:
    """Every ModelAssumptions field, keyed by its own field name.

    Field names are read from the model itself, not a hand-maintained list.
    """
    values: dict[str, Decimal] = {}
    for field_name in ModelAssumptions.model_fields:
        value = getattr(assumptions, field_name)
        values[field_name] = value if isinstance(value, Decimal) else Decimal(value)
    return values


def run_forecast(
    assumptions: ModelAssumptions,
    periods: list[ForecastPeriod],
    line_items: list[FinancialLineItem],
) -> ForecastResult:
    """Calculate every line item across every period, in dependency order.

    Reads `assumptions` and `line_items`; mutates neither.
    """
    graph = build_graph(line_items)
    order = calculation_order(graph)
    line_items_by_id = {item.id: item for item in line_items}
    assumption_values = _assumption_values(assumptions)

    values_by_line_item: dict[str, list[PeriodValue]] = {
        line_item_id: [] for line_item_id in order
    }
    previous_values: dict[str, Decimal] = {}

    for period_index, period in enumerate(periods):
        current_values: dict[str, Decimal] = dict(assumption_values)
        context = EvaluationContext(
            current_values=current_values, previous_values=previous_values
        )
        is_first_period = period_index == 0

        for line_item_id in order:
            line_item = line_items_by_id[line_item_id]
            expression = line_item.formula
            if is_first_period and line_item.initial_formula is not None:
                expression = line_item.initial_formula
            if expression is None:
                raise MissingFormulaError(line_item_id, period.id)

            value = evaluate(expression, context)
            current_values[line_item_id] = value
            values_by_line_item[line_item_id].append(
                PeriodValue(period_id=period.id, value=value)
            )

        previous_values = {
            line_item_id: current_values[line_item_id] for line_item_id in order
        }

    line_item_results = [
        LineItemResult(line_item_id=line_item_id, values=values_by_line_item[line_item_id])
        for line_item_id in order
    ]
    return ForecastResult(periods=list(periods), line_items=line_item_results)
