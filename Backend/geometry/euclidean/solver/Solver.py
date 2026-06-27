from .registry import get_operation
from .exceptions import (
    OperationNotFoundError,
    SolverError,
)


class Solver:
    """
    Handles execution of mathematical operations.
    """

    def solve(self, operation, data):

        function = get_operation(operation)

        if function is None:
            raise OperationNotFoundError(
                f"'{operation}' is not a supported operation."
            )

        try:
            result = function(**data)
            return result

        except Exception as e:
            raise SolverError(str(e))