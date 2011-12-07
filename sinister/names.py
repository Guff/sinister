from sinister.config import conf

import builtins
import math

functions = {name: func for name, func in vars(math).items() if callable(func)}
functions.update({"pow": builtins.pow,
                  "min": builtins.min,
                  "max": builtins.max,
                  "round": builtins.round,
                  "abs": builtins.abs
                  })

constants = {name: vars(math)[name] for name in ['pi', 'e']}

names = conf.defined_names.names
names.update(functions)
names.update(constants)
