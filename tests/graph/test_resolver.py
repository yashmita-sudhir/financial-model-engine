from financial_model_engine.domain import FinancialStatementType, Unit
from financial_model_engine.domain import FinancialLineItem as LineItem
from financial_model_engine.graph import (
    GraphNodeType,
    build_graph,
    calculation_order,
    full_order,
    upstream_dependencies,
)


def item(id_, deps=()):
    return LineItem(
        id=id_,
        name=id_,
        statement_type=FinancialStatementType.INCOME_STATEMENT,
        unit=Unit.CURRENCY,
        dependencies=list(deps),
    )


def build_example_graph():
    return build_graph(
        [
            item("customers", ["starting_customers", "customer_growth"]),
            item("revenue", ["customers", "monthly_price"]),
        ]
    )


def assert_respects_edges(graph, order):
    positions = {node_id: i for i, node_id in enumerate(order)}
    for source, target in graph.edges:
        assert positions[source] < positions[target], (source, target)


def test_full_topological_order_respects_every_edge():
    graph = build_example_graph()
    order = full_order(graph)
    assert set(order) == set(graph.nodes)
    assert_respects_edges(graph, order)


def test_calculation_only_order_contains_only_line_items():
    graph = build_example_graph()
    order = calculation_order(graph)
    assert all(
        graph.nodes[node_id]["type"] == GraphNodeType.LINE_ITEM for node_id in order
    )
    assert set(order) == {"customers", "revenue"}


def test_calculation_only_order_respects_edges_between_line_items():
    graph = build_graph(
        [
            item("revenue"),
            item("cogs"),
            item("gross_profit", ["revenue", "cogs"]),
            item("tax", ["gross_profit"]),
            item("net_income", ["gross_profit", "tax"]),
        ]
    )
    order = calculation_order(graph)
    positions = {node_id: i for i, node_id in enumerate(order)}
    assert positions["revenue"] < positions["gross_profit"]
    assert positions["cogs"] < positions["gross_profit"]
    assert positions["gross_profit"] < positions["tax"]
    assert positions["gross_profit"] < positions["net_income"]
    assert positions["tax"] < positions["net_income"]


def test_assumptions_precede_dependent_calculations():
    graph = build_example_graph()
    order = full_order(graph)
    positions = {node_id: i for i, node_id in enumerate(order)}
    assert positions["starting_customers"] < positions["customers"]
    assert positions["customer_growth"] < positions["customers"]
    assert positions["monthly_price"] < positions["revenue"]
    assert positions["customers"] < positions["revenue"]


def test_upstream_dependencies_of_revenue():
    graph = build_example_graph()
    upstream = upstream_dependencies(graph, "revenue")
    assert upstream == {
        "customers",
        "starting_customers",
        "customer_growth",
        "monthly_price",
    }


def test_upstream_dependencies_of_independent_node_is_empty():
    graph = build_example_graph()
    assert upstream_dependencies(graph, "starting_customers") == set()
