import symtable

def parse_function(code_str, env):
    lambda_str = 'lambda x: ({})'.format(code_str)
    syms = symtable.symtable(lambda_str, '<function-entry>', 'eval')
    
    for name in syms.get_children()[0].get_globals():
        if name not in env:
            raise NameError("name '{}' is not defined".format(name))
    else:
        return eval(lambda_str, env)
