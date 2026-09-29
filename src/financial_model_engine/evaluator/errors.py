class ExpressionEvaluationError(Exception):
    """Base class for expression-evaluation errors."""


class MissingValueError(ExpressionEvaluationError):
    def __init__(self, stable_id: str):
        self.stable_id = stable_id
        super().__init__(f"no current value available for '{stable_id}'")


class MissingPreviousPeriodValueError(ExpressionEvaluationError):
    def __init__(self, stable_id: str):
        self.stable_id = stable_id
        super().__init__(f"no previous-period value available for '{stable_id}'")


class DivisionByZeroError(ExpressionEvaluationError):
    def __init__(self):
        super().__init__("division by zero in expression evaluation")


class UnsupportedExpressionError(ExpressionEvaluationError):
    def __init__(self, node: object):
        self.node = node
        super().__init__(f"unsupported expression node: {type(node)!r}")
