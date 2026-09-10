from ..engine_loader import load_all_functions
from . import operation_adapters


def get_supported_operations():
    operations = load_all_functions()
    operations.update(
        {
            name: func
            for name, func in vars(operation_adapters).items()
            if callable(func) and not name.startswith("_")
        }
    )
    return {name: func for name, func in sorted(operations.items())}


SUPPORTED_OPERATIONS = get_supported_operations()


def _ensure_supported_operations():
    return SUPPORTED_OPERATIONS
