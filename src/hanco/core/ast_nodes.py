class Program:
    def __init__(self, statements, line=None):
        self.statements = statements
        self.line = line

class Function:
    def __init__(self, name, params, body, line=None):
        self.name = name
        self.params = params
        self.body = body
        self.line = line

class Call:
    def __init__(self, name, args, line=None):
        self.name = name
        self.args = args
        self.line = line

class Return:
    def __init__(self, value, line=None):
        self.value = value
        self.line = line

class Binary:
    def __init__(self, left, op, right, line=None):
        self.left = left
        self.op = op
        self.right = right
        self.line = line

class Literal:
    def __init__(self, value, line=None):
        self.value = value
        self.line = line

class Var:
    def __init__(self, name, line=None):
        self.name = name
        self.line = line

class Index:
    def __init__(self, target, index, line=None):
        self.target = target
        self.index = index
        self.line = line

class MethodCall:
    def __init__(self, target, method, args, line=None):
        self.target = target
        self.method = method
        self.args = args
        self.line = line

class If:
    def __init__(self, branches, else_branch, line=None):
        self.branches = branches
        self.else_branch = else_branch
        self.line = line

class Try:
    def __init__(self, try_body, error_name, catch_body, finally_body, line=None):
        self.try_body = try_body
        self.error_name = error_name
        self.catch_body = catch_body
        self.finally_body = finally_body
        self.line = line

class ListDecl:
    def __init__(self, name, items, line=None):
        self.name = name
        self.items = items
        self.line = line

class VarDecl:
    def __init__(self, type_name, name, value, line=None):
        self.type_name = type_name
        self.name = name
        self.value = value
        self.line = line

class Assign:
    def __init__(self, name, value, line=None):
        self.name = name
        self.value = value
        self.line = line

class IndexAssign:
    def __init__(self, target, index, value, line=None):
        self.target = target
        self.index = index
        self.value = value
        self.line = line

class WhileLoop:
    def __init__(self, condition, body, line=None):
        self.condition = condition
        self.body = body
        self.line = line

class ForLoop:
    def __init__(self, var_name, start, end, body, line=None):
        self.var_name = var_name
        self.start = start
        self.end = end
        self.body = body
        self.line = line

class Break:
    def __init__(self, line=None):
        self.line = line

class Continue:
    def __init__(self, line=None):
        self.line = line

class Use:
    def __init__(self, names, line=None):
        self.names = names
        self.line = line
