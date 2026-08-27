import inspect

from .registry import get_operation
from .exceptions import (
    InvalidParametersError,
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
            inspect.signature(function).bind(**data)
        except TypeError as exc:
            raise InvalidParametersError(str(exc)) from exc

        try:
            result = function(**data)
        except (TypeError, ValueError, ZeroDivisionError) as exc:
            raise InvalidParametersError(str(exc)) from exc
        except Exception as exc:
            raise SolverError("The geometry operation failed.") from exc

        return result