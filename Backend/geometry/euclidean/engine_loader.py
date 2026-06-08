import importlib
import pkgutil
from . import Math_Engine


def load_all_functions():
    functions = {}

    package = Math_Engine

    # loop through all modules in the local Math_Engine package
    for loader, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package.__name__}.{module_name}")

        for attr in dir(module):
            func = getattr(module, attr)

            if callable(func) and not attr.startswith("_"):
                # store function
                functions[attr] = func

    return functions