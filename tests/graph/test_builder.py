import pytest

from financial_model_engine.domain import FinancialStatementType, ModelAssumptions, Unit
from financial_model_engine.domain import FinancialLineItem as LineItem
from financial_model_engine.graph import (
    CircularDependencyError,
    DuplicateGraphNodeError,
    GraphNodeType,
    MissingDependencyError,
    SelfDependencyError,
    assumption_ids,
    build_graph,
    get_node,
)


def item(id_, deps=()):
    return LineItem(
        id=id_,
        name=id_,
        statement_type=FinancialStatementType.INCOME_STATEMENT,
        unit=Unit.CURRENCY,
        dependencies=list(deps),
    )


def test_assumption_nodes_are_registered():
    graph = build_graph([])
    assert assumption_ids() <= set(graph.nodes)
    assert "monthly_price" in graph.nodes


def test_line_item_nodes_are_registered():
    graph = build_graph([item("customers")])
    assert "customers" in graph.nodes


def test_node_type_metadata_is_correct():
    graph = build_graph([item("customers")])
    assert get_node(graph, "monthly_price").type == GraphNodeType.ASSUMPTION
    assert get_node(graph, "customers").type == GraphNodeType.LINE_ITEM


def test_line_item_depending_on_assumption():
    graph = build_graph([item("revenue", ["monthly_price"])])
    assert graph.has_edge("monthly_price", "revenue")


def test_line_item_depending_on_line_item():
    graph = build_graph([item("customers"), item("revenue", ["customers"])])
    assert graph.has_edge("customers", "revenue")


def test_line_item_depending_on_both():
    graph = build_graph(
        [item("customers"), item("revenue", ["customers", "monthly_price"])]
    )
    assert graph.has_edge("customers", "revenue")
    assert graph.has_edge("monthly_price", "revenue")


def test_multiple_dependencies_feeding_one_item():
    graph = build_graph(
        [item("customers", ["starting_customers", "customer_growth"])]
    )
    assert graph.has_edge("starting_customers", "customers")
    assert graph.has_edge("customer_growth", "customers")


def test_multi_level_chain():
    graph = build_graph(
        [
            item("customers", ["starting_customers"]),
            item("revenue", ["customers", "monthly_price"]),
            item("gross_profit", ["revenue"]),
        ]
    )
    assert graph.has_edge("starting_customers", "customers")
    assert graph.has_edge("customers", "revenue")
    assert graph.has_edge("revenue", "gross_profit")


def test_missing_dependency_rejected():
    with pytest.raises(MissingDependencyError) as exc_info:
        build_graph([item("customers"), item("revenue", ["customers", "price"])])
    assert exc_info.value.line_item_id == "revenue"
    assert exc_info.value.missing_dependency_id == "price"


def test_self_dependency_rejected():
    with pytest.raises(SelfDependencyError) as exc_info:
        build_graph([item("revenue", ["revenue"])])
    assert exc_info.value.line_item_id == "revenue"


def test_duplicate_id_across_assumption_and_line_item_rejected():
    with pytest.raises(DuplicateGraphNodeError) as exc_info:
        build_graph([item("monthly_price")])
    assert exc_info.value.node_id == "monthly_price"


def test_two_node_cycle_rejected():
    with pytest.raises(CircularDependencyError) as exc_info:
        build_graph([item("a", ["b"]), item("b", ["a"])])
    assert set(exc_info.value.cycle_ids) == {"a", "b"}


def test_three_node_cycle_rejected():
    with pytest.raises(CircularDependencyError) as exc_info:
        build_graph([item("a", ["c"]), item("b", ["a"]), item("c", ["b"])])
    assert set(exc_info.value.cycle_ids) == {"a", "b", "c"}


def test_custom_assumptions_type_can_be_supplied():
    class NarrowAssumptions(ModelAssumptions):
        pass

    graph = build_graph([], assumptions_type=NarrowAssumptions)
    assert assumption_ids(NarrowAssumptions) <= set(graph.nodes)


def test_input_line_items_are_not_mutated():
    revenue = item("revenue", ["monthly_price"])
    original_deps = list(revenue.dependencies)
    build_graph([revenue])
    assert revenue.dependencies == original_deps
