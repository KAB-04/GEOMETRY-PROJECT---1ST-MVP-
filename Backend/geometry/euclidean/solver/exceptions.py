# solver/exceptions.py

class SolverError(Exception):
    """
   Base exception for all solver-related errors.
    """
    pass


class OperationNotFoundError(SolverError):
    """
   Raised when the requested operation does not exist.
    """
    pass


class InvalidParametersError(SolverError):
    """
   Raised when supplied parameters are invalid.
    """
    pass