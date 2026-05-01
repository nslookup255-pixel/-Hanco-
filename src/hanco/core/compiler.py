from ast_nodes import *

class Compiler:
    def __init__(self):
        print(":: 한코 컴파일 시작 ::")
        self.code=[]
        self.funcs={}
        self.label_counter=0
        self.loop_stack=[]

    def emit(self,o,a=None):
        self.code.append((o,a))

    def new_label(self, prefix="L"):
        label = f"{prefix}{self.label_counter}"
        self.label_counter += 1
        return label

    def compile(self,node):
        if isinstance(node,Program):

            main=[]
            funcs=[]

            for s in node.s:
                if isinstance(s,Function): funcs.append(s)
                else: main.append(s)

            self.emit("JMP","MAIN")

            for f in funcs:
                self.funcs[f.n]=(len(self.code),f.p)
                self.emit("FUNC",(f.n, list(f.p)))

                for p in reversed(f.p):
                    self.emit("STORE",p)

                for s in f.b:
                    self.compile(s)

                self.emit("RET")

            self.emit("LABEL","MAIN")

            for s in main:
                self.compile(s)

        elif isinstance(node,ListDecl):
            for item in node.items:
                self.compile(item)
            self.emit("MAKE_LIST",len(node.items))
            self.emit("DECLARE",(node.name,"목록"))

        elif isinstance(node,Call):
            for a in node.a:
                self.compile(a)
            self.emit("CALL",(node.n, len(node.a)))

        elif isinstance(node,Return):
            self.compile(node.v)
            self.emit("RET")

        elif isinstance(node, If):
            end_label = self.new_label("IF_END_")

            for i, (cond, body) in enumerate(node.branches):
                next_label = self.new_label(f"IF_NEXT_{i}_")

                self.compile(cond)
                self.emit("JMP_IF_FALSE", next_label)

                for s in body:
                    self.compile(s)

                self.emit("JMP", end_label)
                self.emit("LABEL", next_label)

            # else
            for s in node.else_branch:
                self.compile(s)

            self.emit("LABEL", end_label)

        elif isinstance(node, WhileLoop):
            start_label = self.new_label("WHILE_START_")
            end_label = self.new_label("WHILE_END_")

            self.loop_stack.append((end_label, start_label))
            self.emit("LABEL", start_label)
            self.compile(node.condition)
            self.emit("JMP_IF_FALSE", end_label)

            for s in node.body:
                self.compile(s)

            self.emit("JMP", start_label)
            self.emit("LABEL", end_label)
            self.loop_stack.pop()

        elif isinstance(node, ForLoop):
            end_name = self.new_label("@for_end_")
            direction_check = self.new_label("FOR_DIRECTION_")
            continue_dispatch = self.new_label("FOR_CONTINUE_")
            asc_check = self.new_label("FOR_ASC_CHECK_")
            asc_body = self.new_label("FOR_ASC_BODY_")
            asc_step = self.new_label("FOR_ASC_STEP_")
            desc_check = self.new_label("FOR_DESC_CHECK_")
            desc_body = self.new_label("FOR_DESC_BODY_")
            desc_step = self.new_label("FOR_DESC_STEP_")
            end_label = self.new_label("FOR_END_")

            self.compile(node.start)
            self.emit("DECLARE", (node.var_name, "숫자"))

            self.compile(node.end)
            self.emit("DECLARE", (end_name, "숫자"))

            self.emit("JMP", direction_check)

            self.emit("LABEL", direction_check)
            self.emit("LOAD", node.var_name)
            self.emit("LOAD", end_name)
            self.emit("<=", None)
            self.emit("JMP_IF_FALSE", desc_check)
            self.emit("JMP", asc_check)

            self.loop_stack.append((end_label, continue_dispatch))
            self.emit("LABEL", asc_check)
            self.emit("LOAD", node.var_name)
            self.emit("LOAD", end_name)
            self.emit("<=", None)
            self.emit("JMP_IF_FALSE", end_label)
            self.emit("JMP", asc_body)

            self.emit("LABEL", asc_body)

            for s in node.body:
                self.compile(s)

            self.emit("LABEL", asc_step)
            self.emit("LOAD", node.var_name)
            self.emit("PUSH", 1)
            self.emit("+", None)
            self.emit("ASSIGN", node.var_name)
            self.emit("JMP", asc_check)

            self.emit("LABEL", desc_check)
            self.emit("LOAD", node.var_name)
            self.emit("LOAD", end_name)
            self.emit(">=", None)
            self.emit("JMP_IF_FALSE", end_label)
            self.emit("JMP", desc_body)

            self.emit("LABEL", desc_body)

            for s in node.body:
                self.compile(s)

            self.emit("LABEL", desc_step)
            self.emit("LOAD", node.var_name)
            self.emit("PUSH", 1)
            self.emit("-", None)
            self.emit("ASSIGN", node.var_name)
            self.emit("JMP", desc_check)

            self.emit("LABEL", continue_dispatch)
            self.emit("LOAD", node.var_name)
            self.emit("LOAD", end_name)
            self.emit("<=", None)
            self.emit("JMP_IF_FALSE", desc_step)
            self.emit("JMP", asc_step)

            self.emit("LABEL", end_label)
            self.loop_stack.pop()

        elif isinstance(node,Binary):
            self.compile(node.l)
            self.compile(node.r)
            self.emit(node.o)

        elif isinstance(node,Literal):
            self.emit("PUSH",node.v)

        elif isinstance(node,Var):
            self.emit("LOAD",node.n)

        elif isinstance(node,Index):
            self.compile(node.target)
            self.compile(node.index)
            self.emit("INDEX")

        elif isinstance(node,MethodCall):
            self.compile(node.target)
            for arg in node.args:
                self.compile(arg)
            self.emit("METHOD_CALL", (node.method, len(node.args)))

        elif isinstance(node, VarDecl):
            self.compile(node.value)
            self.emit("DECLARE", (node.name, node.type_name))

        elif isinstance(node, Assign):
            self.compile(node.value)
            self.emit("ASSIGN", node.name)

        elif isinstance(node, IndexAssign):
            self.compile(node.target)
            self.compile(node.index)
            self.compile(node.value)
            self.emit("INDEX_ASSIGN")

        elif isinstance(node, Break):
            if not self.loop_stack:
                raise Exception("멈춤은 반복문 안에서만 사용할 수 있습니다.")
            break_label, _ = self.loop_stack[-1]
            self.emit("JMP", break_label)

        elif isinstance(node, Continue):
            if not self.loop_stack:
                raise Exception("건너뛰기는 반복문 안에서만 사용할 수 있습니다.")
            _, continue_label = self.loop_stack[-1]
            self.emit("JMP", continue_label)


    def get(self):
        return self.code
