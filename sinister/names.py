from sinister.config import conf

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

import math

functions = {name: func for name, func in vars(math).items() if callable(func)}
functions.update({"pow": builtins.pow,
                  "min": builtins.min,
                  "max": builtins.max,
                  "round": builtins.round,
                  "abs": builtins.abs,
                  "sum": builtins.sum
                  })

constants = {name: vars(math)[name] for name in ['pi', 'e']}

names = conf.defined_names.names
names.update(functions)
names.update(constants)
