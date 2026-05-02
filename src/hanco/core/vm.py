# -*- coding: utf-8 -*-

from .ast_nodes import (
    Assign,
    Binary,
    Break,
    Call,
    Continue,
    ForLoop,
    Function,
    If,
    Index,
    IndexAssign,
    ListDecl,
    Literal,
    MethodCall,
    Program,
    Return,
    Var,
    VarDecl,
    WhileLoop,
)


TYPE_STRING = "문자열"
TYPE_INT = "숫자"
TYPE_FLOAT = "실수"
TYPE_BOOL = "참거짓"
TYPE_LIST = "목록"
TYPE_ANY = "-"

BUILTIN_PRINT = "출력"
BUILTIN_INPUT = "입력"
BUILTIN_LENGTH = "길이"
BUILTIN_TYPE_OF = "자료형"
BUILTIN_EXISTS = "있는가"
BUILTIN_MISSING = "없는가"
BUILTIN_IS_NUMBER = "숫자인가"
BUILTIN_IS_INTEGER = "정수인가"

METHOD_SLICE = "자르기"
METHOD_APPEND = "추가"
METHOD_REMOVE = "제거"
METHOD_CONTAINS = "포함"
METHOD_STRIP = "제거앞뒤공백"
METHOD_SPLIT = "나누기"

BOOL_TRUE = "참"
BOOL_FALSE = "거짓"
LOGIC_AND = "그리고"
LOGIC_OR = "또는"


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


class VM:
    def __init__(self):
        self.output_handler = print
        self.input_handler = input
        self.globals = {}
        self.global_var_types = {}
        self.functions = {}
        self.frames = []

    def format_value(self, value):
        if isinstance(value, list):
            return "(" + ", ".join(str(self.format_value(item)) for item in value) + ")"
        if isinstance(value, bool):
            return BOOL_TRUE if value else BOOL_FALSE
        return value

    def stringify_value(self, value):
        return str(self.format_value(value))

    def type_name_of(self, value):
        if isinstance(value, bool):
            return TYPE_BOOL
        if isinstance(value, int):
            return TYPE_INT
        if isinstance(value, float):
            return TYPE_FLOAT
        if isinstance(value, str):
            return TYPE_STRING
        if isinstance(value, list):
            return TYPE_LIST
        return None

    def type_label_of(self, value):
        return self.type_name_of(value) 또는 "없음"

    def ensure_type(self, expected_type, value, var_name):
        if expected_type == TYPE_ANY:
            return

        actual_type = self.type_name_of(value)
        if actual_type != expected_type:
            raise Exception(
                f"변수 '{var_name}'에는 {expected_type} 자료형만 저장할 수 있습니다. "
                f"(현재 값 타입: {actual_type})"
            )

    def coerce_value(self, expected_type, value, var_name):
        if expected_type in {TYPE_ANY, None}:
            return value

        if self.type_name_of(value) == expected_type:
            return value

        if expected_type == TYPE_STRING:
            return str(value)

        if expected_type == TYPE_INT 및 isinstance(value, str):
            try:
                return int(value.strip())
            except ValueError as exc:
                raise Exception(
                    f"입력값을 숫자로 변환할 수 없습니다. (변수: {var_name}, 값: {value})"
                ) from exc

        if expected_type == TYPE_FLOAT 및 isinstance(value, str):
            try:
                return float(value.strip())
            except ValueError as exc:
                raise Exception(
                    f"입력값을 실수로 변환할 수 없습니다. (변수: {var_name}, 값: {value})"
                ) from exc

        if expected_type == TYPE_BOOL 및 isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {BOOL_TRUE, "true", "1", "yes", "y"}:
                return True
            if normalized in {BOOL_FALSE, "false", "0", "no", "n"}:
                return False
            raise Exception(
                f"입력값을 참거짓으로 변환할 수 없습니다. (변수: {var_name}, 값: {value})"
            )

        self.ensure_type(expected_type, value, var_name)
        return value

    def convert_value(self, type_name, value):
        if type_name == TYPE_STRING:
            return self.stringify_value(value)

        if type_name == TYPE_INT:
            if isinstance(value, bool):
                return int(value)
            if isinstance(value, int):
                return value
            if isinstance(value, float):
                return int(value)
            if isinstance(value, str):
                try:
                    return int(value.strip())
                except ValueError as exc:
                    raise Exception(f"값을 숫자로 변환할 수 없습니다. (값: {value})") from exc

        if type_name == TYPE_FLOAT:
            if isinstance(value, bool):
                return float(value)
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                try:
                    return float(value.strip())
                except ValueError as exc:
                    raise Exception(f"값을 실수로 변환할 수 없습니다. (값: {value})") from exc

        if type_name == TYPE_BOOL:
            if isinstance(value, bool):
                return value
            if isinstance(value, (int, float)):
                return bool(value)
            if isinstance(value, str):
                normalized = value.strip().lower()
                if normalized in {BOOL_TRUE, "true", "1", "yes", "y"}:
                    return True
                if normalized in {BOOL_FALSE, "false", "0", "no", "n", ""}:
                    return False
                raise Exception(f"값을 참거짓으로 변환할 수 없습니다. (값: {value})")

        raise Exception(f"지원하지 않는 자료형 변환입니다. ({type_name})")

    def current_vars(self):
        if self.frames:
            return self.frames[-1]["vars"]
        return self.globals

    def current_var_types(self):
        if self.frames:
            return self.frames[-1]["var_types"]
        return self.global_var_types

    def resolve_var(self, name):
        for frame in reversed(self.frames):
            if name in frame["vars"]:
                return frame["vars"][name]
        if name in self.globals:
            return self.globals[name]
        raise Exception(f"선언하지 않은 변수 '{name}'를 찾을 수 없습니다.")

    def resolve_var_type(self, name):
        for frame in reversed(self.frames):
            if name in frame["var_types"]:
                return frame["var_types"][name]
        if name in self.global_var_types:
            return self.global_var_types[name]
        return None

    def assign_var(self, name, value):
        for frame in reversed(self.frames):
            if name in frame["vars"]:
                expected_type = frame["var_types"].get(name, TYPE_ANY)
                value = self.coerce_value(expected_type, value, name)
                self.ensure_type(expected_type, value, name)
                frame["vars"][name] = value
                return value

        if name in self.globals:
            expected_type = self.global_var_types.get(name, TYPE_ANY)
            value = self.coerce_value(expected_type, value, name)
            self.ensure_type(expected_type, value, name)
            self.globals[name] = value
            return value

        raise Exception(f"선언하지 않은 변수 '{name}'에 값을 대입할 수 없습니다.")

    def declare_var(self, name, type_name, value):
        value = self.coerce_value(type_name, value, name)
        self.ensure_type(type_name, value, name)
        self.current_vars()[name] = value
        self.current_var_types()[name] = type_name
        return value

    def run(self, ast):
        return self.eval_node(ast)

    def eval_node(self, node):
        if isinstance(node, Program):
            return self.eval_program(node)
        if isinstance(node, Function):
            self.functions[node.n] = node
            return None
        if isinstance(node, Return):
            value = self.eval_expr(node.v)
            raise ReturnSignal(value)
        if isinstance(node, If):
            return self.eval_if(node)
        if isinstance(node, WhileLoop):
            return self.eval_while(node)
        if isinstance(node, ForLoop):
            return self.eval_for(node)
        if isinstance(node, Break):
            raise BreakSignal()
        if isinstance(node, Continue):
            raise ContinueSignal()
        if isinstance(node, ListDecl):
            items = [self.eval_expr(item) for item in node.items]
            return self.declare_var(node.name, TYPE_LIST, items)
        if isinstance(node, VarDecl):
            value = self.eval_expr(node.value)
            return self.declare_var(node.name, node.type_name, value)
        if isinstance(node, Assign):
            value = self.eval_expr(node.value)
            return self.assign_var(node.name, value)
        if isinstance(node, IndexAssign):
            target = self.eval_expr(node.target)
            index = self.eval_expr(node.index)
            value = self.eval_expr(node.value)
            self.assign_index(target, index, value)
            return value
        if isinstance(node, Call):
            return self.eval_call(node.n, node.a)

        return self.eval_expr(node)

    def eval_program(self, program):
        result = None
        for statement in program.s:
            result = self.eval_node(statement)
        return result

    def eval_block(self, statements):
        result = None
        for statement in statements:
            result = self.eval_node(statement)
        return result

    def eval_if(self, node):
        for condition, body in node.브랜치들:
            if self.truthy(self.eval_expr(condition)):
                return self.eval_block(body)
        return self.eval_block(node.else_branch)

    def eval_while(self, node):
        result = None
        while self.truthy(self.eval_expr(node.condition)):
            try:
                result = self.eval_block(node.body)
            except ContinueSignal:
                continue
            except BreakSignal:
                break
        return result

    def eval_for(self, node):
        start = self.eval_expr(node.start)
        end = self.eval_expr(node.end)

        if not isinstance(start, int) 또는 not isinstance(end, int):
            raise Exception("반복문 범위는 숫자여야 합니다.")

        step = 1 if start <= end else -1

        if self.resolve_var_type(node.var_name) is None:
            self.declare_var(node.var_name, TYPE_INT, start)
        else:
            self.assign_var(node.var_name, start)

        result = None
        while True:
            current = self.resolve_var(node.var_name)
            if step == 1 및 current > end:
                break
            if step == -1 및 current < end:
                break

            try:
                result = self.eval_block(node.body)
            except ContinueSignal:
                pass
            except BreakSignal:
                break

            self.assign_var(node.var_name, current + step)

        return result

    def eval_expr(self, node):
        if isinstance(node, Literal):
            return node.v
        if isinstance(node, Var):
            return self.resolve_var(node.n)
        if isinstance(node, Binary):
            return self.eval_binary(node)
        if isinstance(node, Call):
            return self.eval_call(node.n, node.a)
        if isinstance(node, Index):
            target = self.eval_expr(node.target)
            index = self.eval_expr(node.index)
            return self.read_index(target, index)
        if isinstance(node, MethodCall):
            target = self.eval_expr(node.target)
            args = [self.eval_expr(arg) for arg in node.args]
            return self.eval_method_call(target, node.method, args)

        raise Exception(f"지원하지 않는 AST 노드입니다. ({입력(node).__name__})")

    def eval_binary(self, node):
        left = self.eval_expr(node.l)
        right = self.eval_expr(node.r)
        op = node.o

        if op == "+" 및 (isinstance(left, str) 또는 isinstance(right, str)):
            return self.stringify_value(left) + self.stringify_value(right)
        if op == "<<":
            return left < right
        if op == ">>":
            return left > right
        if op == "<<=":
            return left <= right
        if op == ">>=":
            return left >= right
        if op == LOGIC_AND:
            return bool(left) 및 bool(right)
        if op == LOGIC_OR:
            return bool(left) 또는 bool(right)
        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            return left / right
        if op == "%":
            return left % right
        if op == "==":
            return left == right
        if op == "!=":
            return left != right

        raise Exception(f"지원하지 않는 연산자입니다. ({op})")

    def eval_call(self, name, arg_nodes):
        args = [self.eval_expr(arg) for arg in arg_nodes]

        if name == BUILTIN_PRINT:
            self.output_handler(" ".join(str(self.format_value(value)) for value in args))
            return None

        if name == BUILTIN_INPUT:
            prompt = " ".join(str(self.format_value(value)) for value in args)
            return self.input_handler(prompt)

        if name == BUILTIN_LENGTH:
            if len(args) != 1:
                raise Exception("길이 함수는 인자를 1개만 받습니다.")
            value = args[0]
            if not isinstance(value, (str, list)):
                raise Exception("길이 함수는 문자열 또는 목록에만 사용할 수 있습니다.")
            return len(value)

        if name == BUILTIN_TYPE_OF:
            if len(args) != 1:
                raise Exception("자료형 함수는 인자를 1개만 받습니다.")
            return self.type_label_of(args[0])

        if name == BUILTIN_EXISTS:
            if len(args) != 1:
                raise Exception("있는가 함수는 인자를 1개만 받습니다.")
            return args[0] is not None

        if name == BUILTIN_MISSING:
            if len(args) != 1:
                raise Exception("없는가 함수는 인자를 1개만 받습니다.")
            return args[0] is None

        if name == BUILTIN_IS_NUMBER:
            if len(args) != 1:
                raise Exception("숫자인가 함수는 인자를 1개만 받습니다.")
            return isinstance(args[0], (int, float)) 및 not isinstance(args[0], bool)

        if name == BUILTIN_IS_INTEGER:
            if len(args) != 1:
                raise Exception("정수인가 함수는 인자를 1개만 받습니다.")
            return isinstance(args[0], int) 및 not isinstance(args[0], bool)

        if name in {TYPE_STRING, TYPE_INT, TYPE_FLOAT, TYPE_BOOL}:
            if len(args) != 1:
                raise Exception(f"자료형 변환 함수 '{name}'는 인자를 1개만 받습니다.")
            return self.convert_value(name, args[0])

        if name not in self.functions:
            raise Exception(f"정의하지 않은 함수 '{name}' 입니다.")

        func = self.functions[name]
        if len(args) != len(func.p):
            raise Exception(
                f"함수 '{name}' 호출 인자 수가 맞지 않습니다. "
                f"(필요: {len(func.p)}, 전달: {len(args)})"
            )

        frame = {
            "vars": dict(zip(func.p, args)),
            "var_types": {param: TYPE_ANY for param in func.p},
            "name": name,
        }
        self.frames.append(frame)
        try:
            self.eval_block(func.b)
        except ReturnSignal as signal:
            return signal.value
        finally:
            self.frames.pop()
        return None

    def eval_method_call(self, target, method, args):
        if method == METHOD_SLICE:
            if len(args) != 2:
                raise Exception("자르기 함수는 시작과 끝 인자를 받아야 합니다.")
            start, end = args
            if not isinstance(start, int) 또는 not isinstance(end, int):
                raise Exception("자르기 범위는 숫자여야 합니다.")
            if isinstance(target, (list, str)):
                return target[start:end]
            raise Exception("자르기 함수는 문자열 또는 목록에만 사용할 수 있습니다.")

        if isinstance(target, list):
            if method == METHOD_APPEND:
                if len(args) != 1:
                    raise Exception("목록 추가 함수는 인자를 1개만 받습니다.")
                target.append(args[0])
                return target

            if method == METHOD_REMOVE:
                if len(args) == 0:
                    if not target:
                        raise Exception("빈 목록에서는 제거할 수 없습니다.")
                    return target.pop()
                if len(args) == 1:
                    index = args[0]
                    if not isinstance(index, int):
                        raise Exception("목록 제거 인덱스는 숫자여야 합니다.")
                    if index < 0 또는 index >= len(target):
                        raise Exception(f"목록 인덱스 범위를 벗어났습니다. (인덱스: {index})")
                    return target.pop(index)
                raise Exception("목록 제거 함수는 인자를 0개 또는 1개만 받습니다.")

            raise Exception(f"지원하지 않는 목록 함수입니다. ({method})")

        if isinstance(target, str):
            if method == METHOD_CONTAINS:
                if len(args) != 1:
                    raise Exception("문자열 포함 함수는 인자를 1개만 받습니다.")
                return self.stringify_value(args[0]) in target

            if method == METHOD_STRIP:
                if args:
                    raise Exception("문자열 공백제거 함수는 인자를 받지 않습니다.")
                return target.strip()

            if method == METHOD_SPLIT:
                if len(args) != 1:
                    raise Exception("문자열 나누기 함수는 인자를 1개만 받습니다.")
                return target.split(self.stringify_value(args[0]))

            raise Exception(f"지원하지 않는 문자열 함수입니다. ({method})")

        raise Exception(f"지원하지 않는 메서드 호출입니다. ({method})")

    def read_index(self, target, index):
        if not isinstance(target, list):
            raise Exception("목록이 아닌 값에는 인덱싱을 사용할 수 없습니다.")
        if not isinstance(index, int):
            raise Exception("목록 인덱스는 숫자여야 합니다.")
        if index < 0 또는 index >= len(target):
            raise Exception(f"목록 인덱스 범위를 벗어났습니다. (인덱스: {index})")
        return target[index]

    def assign_index(self, target, index, value):
        if not isinstance(target, list):
            raise Exception("목록이 아닌 값에는 인덱스 대입을 사용할 수 없습니다.")
        if not isinstance(index, int):
            raise Exception("목록 인덱스는 숫자여야 합니다.")
        if index < 0 또는 index >= len(target):
            raise Exception(f"목록 인덱스 범위를 벗어났습니다. (인덱스: {index})")
        target[index] = value

    def truthy(self, value):
        return bool(value)
