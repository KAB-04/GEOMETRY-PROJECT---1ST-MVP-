import importlib
import inspect
import pkgutil
from . import Math_Engine


def load_all_functions():
    functions = {}

    package = Math_Engine

    # loop through all modules in the local Math_Engine package
    for loader, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package.__name__}.{module_name}")

        for attr, value in vars(module).items():
            if attr.startswith("_"):
                continue

            if inspect.isfunction(value):
                functions[attr] = value

    return functions