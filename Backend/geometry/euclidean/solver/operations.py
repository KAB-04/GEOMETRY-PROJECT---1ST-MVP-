from ..engine_loader import load_all_functions


SUPPORTED_OPERATIONS = None


def get_supported_operations():
    return {name: func for name, func in sorted(load_all_functions().items())}


def _ensure_supported_operations():
    global SUPPORTED_OPERATIONS
    if SUPPORTED_OPERATIONS is None:
        SUPPORTED_OPERATIONS = get_supported_operations()
    return SUPPORTED_OPERATIONS