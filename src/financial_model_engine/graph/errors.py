class GraphError(Exception):
    """Base class for dependency-graph errors."""


class MissingDependencyError(GraphError):
    def __init__(self, line_item_id: str, missing_dependency_id: str):
        self.line_item_id = line_item_id
        self.missing_dependency_id = missing_dependency_id
        super().__init__(
            f"line item '{line_item_id}' depends on unknown id "
            f"'{missing_dependency_id}'"
        )


class SelfDependencyError(GraphError):
    def __init__(self, line_item_id: str):
        self.line_item_id = line_item_id
        super().__init__(f"line item '{line_item_id}' depends on itself")


class DuplicateGraphNodeError(GraphError):
    def __init__(self, node_id: str):
        self.node_id = node_id
        super().__init__(
            f"id '{node_id}' is used by both an assumption and a line item"
        )


class CircularDependencyError(GraphError):
    def __init__(self, cycle_ids: list[str]):
        self.cycle_ids = cycle_ids
        super().__init__(f"circular dependency: {' -> '.join(cycle_ids)}")
