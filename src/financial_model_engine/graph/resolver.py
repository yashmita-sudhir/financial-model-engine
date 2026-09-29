import networkx as nx

from financial_model_engine.graph.nodes import GraphNodeType


def full_order(graph: nx.DiGraph) -> list[str]:
    """A topological order over every node (assumptions and line items)."""
    return list(nx.topological_sort(graph))


def calculation_order(graph: nx.DiGraph) -> list[str]:
    """A topological order over LINE_ITEM nodes only."""
    return [
        node_id
        for node_id in nx.topological_sort(graph)
        if graph.nodes[node_id]["type"] == GraphNodeType.LINE_ITEM
    ]


def upstream_dependencies(graph: nx.DiGraph, node_id: str) -> set[str]:
    """Every node that node_id transitively depends on."""
    return set(nx.ancestors(graph, node_id))
