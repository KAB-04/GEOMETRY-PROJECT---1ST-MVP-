from .operations import _ensure_supported_operations


def get_operation(operation_name):
    """
    Return a registered operation.
    """
    return _ensure_supported_operations().get(operation_name)


def get_all_operations():
    """
    Return all supported operations.
    """
    return _ensure_supported_operations()