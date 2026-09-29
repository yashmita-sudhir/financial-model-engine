from financial_model_engine.domain import FinancialModelDefinition, ModelAssumptions
from financial_model_engine.engine.errors import ModelIntegrityError
from financial_model_engine.engine.protocol import FinanceEngine
from financial_model_engine.engine.result import ModelResult
from financial_model_engine.graph import build_graph, calculation_order


def run_model(
    assumptions: ModelAssumptions,
    model_definition: FinancialModelDefinition,
    engine: FinanceEngine,
) -> ModelResult:
    """Build the dependency graph, resolve calculation order, and run the
    finance engine. Raises ModelIntegrityError if any check fails.
    """
    graph = build_graph(model_definition.line_items)
    order = calculation_order(graph)

    result = engine.run(assumptions, order)

    failed_check_ids = [check.id for check in result.checks if not check.passed]
    if failed_check_ids:
        raise ModelIntegrityError(failed_check_ids)

    return result
