from ..engine_loader import load_all_functions


def get_supported_operations():
    return {name: func for name, func in sorted(load_all_functions().items())}


SUPPORTED_OPERATIONS = get_supported_operations()


def _ensure_supported_operations():
    return SUPPORTED_OPERATIONS