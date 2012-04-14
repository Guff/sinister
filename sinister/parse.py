import ast

class Parser(ast.NodeVisitor):
    def __init__(self, func_str, env):
        self.env = env
        self.func_str = 'lambda x: ({})'.format(func_str)
        self.names = set()
        self.defined_names = set(self.env)
        self.defined_names.add('x')
    
    def visit_Name(self, node):
        self.names.add(node.id)
    
    def validate(self):
        return
        if not self.names.issubset(self.defined_names):
            undefined_names = self.names.difference(self.defined_names)
            raise NameError("undefined names: {}".format(', '.join(undefined_names)))
    
    def create_function(self):
        astree = ast.parse(self.func_str, mode='eval')
        
        self.visit(astree)
        self.validate()
        
        return eval(self.func_str, self.env)
