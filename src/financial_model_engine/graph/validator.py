from collections.abc import Iterable

from financial_model_engine.domain import FinancialLineItem
from financial_model_engine.graph.errors import (
    DuplicateGraphNodeError,
    MissingDependencyError,
    SelfDependencyError,
)


def validate_no_duplicate_ids(
    assumption_ids: set[str], line_item_ids: set[str]
) -> None:
    for node_id in sorted(assumption_ids & line_item_ids):
        raise DuplicateGraphNodeError(node_id)


def validate_dependencies(
    line_items: Iterable[FinancialLineItem], known_ids: set[str]
) -> None:
    for line_item in line_items:
        for dependency_id in line_item.dependencies:
            if dependency_id == line_item.id:
                raise SelfDependencyError(line_item.id)
            if dependency_id not in known_ids:
                raise MissingDependencyError(line_item.id, dependency_id)
