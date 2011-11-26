import builtins
import math

functions = {name: func for name, func in math.__dict__.items() if callable(func)}
functions.update({"pow": builtins.pow, "min": builtins.min, "max": builtins.max})
