class Program:
    def __init__(self, s): self.s = s

class Function:
    def __init__(self, n, p, b):
        self.n=n; self.p=p; self.b=b

class Call:
    def __init__(self, n, a):
        self.n=n; self.a=a

class Return:
    def __init__(self, v): self.v=v

class Binary:
    def __init__(self,l,o,r):
        self.l=l; self.o=o; self.r=r

class Literal:
    def __init__(self,v): self.v=v

class Var:
    def __init__(self,n): self.n=n

class Index:
    def __init__(self, target, index):
        self.target = target
        self.index = index

class MethodCall:
    def __init__(self, target, method, args):
        self.target = target
        self.method = method
        self.args = args

class If:
    def __init__(self, branches, else_branch):
        self.branches = branches  # [(cond, body), ...]
        self.else_branch = else_branch

class ListDecl:
    def __init__(self,name,items):
        self.name=name; self.items=items

class VarDecl:
    def __init__(self,type_name,name,value):
        self.type_name=type_name
        self.name=name
        self.value=value

class Assign:
    def __init__(self,name,value):
        self.name=name
        self.value=value

class IndexAssign:
    def __init__(self, target, index, value):
        self.target = target
        self.index = index
        self.value = value

class WhileLoop:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class ForLoop:
    def __init__(self, var_name, start, end, body):
        self.var_name = var_name
        self.start = start
        self.end = end
        self.body = body

class Break:
    pass

class Continue:
    pass
