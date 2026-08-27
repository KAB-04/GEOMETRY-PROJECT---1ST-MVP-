import importlib
import inspect
import pkgutil
from . import Math_Engine


def load_all_functions():
    functions = {}

    package = Math_Engine

    # loop through all modules in the local Math_Engine package
    for loader, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
        try:
            module = importlib.import_module(f"{package.__name__}.{module_name}")
        except ModuleNotFoundError:
            # A missing optional dependency must not disable unrelated engines.
            continue

        for attr, value in vars(module).items():
            if attr.startswith("_"):
                continue

            if inspect.isfunction(value) and value.__module__ == module.__name__:
                functions[attr] = value

    return functions