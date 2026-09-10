import inspect
import logging

from .registry import get_operation
from .exceptions import (
    InvalidParametersError,
    OperationNotFoundError,
    SolverError,
)

logger = logging.getLogger(__name__)

INVALID_GEOMETRY_PARAMETERS_MESSAGE = (
    "The problem could not be interpreted with all required geometric information."
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

        signature = inspect.signature(function)
        required = [
            name
            for name, parameter in signature.parameters.items()
            if parameter.default is inspect.Parameter.empty
            and parameter.kind
            in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
        ]
        missing = [name for name in required if name not in data]
        if missing:
            logger.warning(
                "Invalid parameters for operation %s. Missing=%s provided=%s",
                operation,
                missing,
                sorted(data.keys()),
            )
            raise InvalidParametersError(INVALID_GEOMETRY_PARAMETERS_MESSAGE)

        try:
            signature.bind(**data)
        except TypeError as exc:
            logger.warning(
                "Invalid parameters for operation %s. Provided=%s error=%s",
                operation,
                sorted(data.keys()),
                exc,
            )
            raise InvalidParametersError(INVALID_GEOMETRY_PARAMETERS_MESSAGE) from exc

        try:
            result = function(**data)
        except (TypeError, ValueError, ZeroDivisionError) as exc:
            logger.warning("Geometry operation %s rejected parameters: %s", operation, exc)
            raise InvalidParametersError(INVALID_GEOMETRY_PARAMETERS_MESSAGE) from exc
        except Exception as exc:
            raise SolverError("The geometry operation failed.") from exc

        return result
