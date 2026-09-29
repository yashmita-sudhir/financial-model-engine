from collections.abc import Iterable
from typing import Any

import networkx as nx

from financial_model_engine.domain import FinancialLineItem, ModelAssumptions
from financial_model_engine.graph.errors import CircularDependencyError
from financial_model_engine.graph.nodes import GraphNode, GraphNodeType
from financial_model_engine.graph.validator import (
    validate_dependencies,
    validate_no_duplicate_ids,
)


def assumption_ids(assumptions_type: type[ModelAssumptions] = ModelAssumptions) -> set[str]:
    """Assumption node IDs, read from the ModelAssumptions field names."""
    return set(assumptions_type.model_fields.keys())


def build_graph(
    line_items: Iterable[FinancialLineItem],
    assumptions_type: type[ModelAssumptions] = ModelAssumptions,
) -> nx.DiGraph:
    """Build the dependency graph. Never mutates the given line items."""
    line_items = list(line_items)
    known_assumption_ids = assumption_ids(assumptions_type)
    line_item_ids = {item.id for item in line_items}

    validate_no_duplicate_ids(known_assumption_ids, line_item_ids)
    validate_dependencies(line_items, known_assumption_ids | line_item_ids)

    graph = nx.DiGraph()
    for node_id in known_assumption_ids:
        graph.add_node(node_id, type=GraphNodeType.ASSUMPTION)
    for item in line_items:
        graph.add_node(item.id, type=GraphNodeType.LINE_ITEM)
    for item in line_items:
        for dependency_id in item.dependencies:
            graph.add_edge(dependency_id, item.id)

    if not nx.is_directed_acyclic_graph(graph):
        cycle = nx.find_cycle(graph)
        cycle_ids = [edge[0] for edge in cycle] + [cycle[-1][1]]
        raise CircularDependencyError(cycle_ids)

    return graph


def get_node(graph: nx.DiGraph, node_id: str) -> GraphNode:
    attrs: dict[str, Any] = graph.nodes[node_id]
    return GraphNode(id=node_id, type=attrs["type"])
