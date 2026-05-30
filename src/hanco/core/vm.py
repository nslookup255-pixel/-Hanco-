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
    Try,
    Use,
    Var,
    VarDecl,
    WhileLoop,
)
from ..std import STDLIB as STANDARD_LIBRARIES


TYPE_STRING = "문자열"
TYPE_INT = "숫자"
TYPE_FLOAT = "실수"
TYPE_BOOL = "참거짓"
TYPE_LIST = "목록"
TYPE_ANY = "자유"
TYPE_ALIASES = {
    "문자": TYPE_STRING,
}

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
LIST_METHOD_ALIASES = {
    "삭제": METHOD_REMOVE,
}
STRING_METHOD_ALIASES = {
    "제거": METHOD_STRIP,
}

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


class StdNamespace:
    def __init__(self, name, handler):
        self.name = name
        self.handler = handler


class VM:
    def __init__(self):
        self.output_handler = print
        self.input_handler = input
        self.globals = {}
        self.global_var_types = {}
        self.functions = {}
        self.frames = []
        self.current_line = None
        self._node_dispatch = {
            Program: self.eval_program,
            Function: self._exec_function,
            Return: self._exec_return,
            If: self.eval_if,
            WhileLoop: self.eval_while,
            ForLoop: self.eval_for,
            Break: self._exec_break,
            Continue: self._exec_continue,
            Use: self._exec_use,
            Try: self._exec_try,
            ListDecl: self._exec_list_decl,
            VarDecl: self._exec_var_decl,
            Assign: self._exec_assign,
            IndexAssign: self._exec_index_assign,
            Call: self._exec_call_node,
        }
        self._expr_dispatch = {
            Literal: self._eval_literal,
            Var: self._eval_var,
            Binary: self.eval_binary,
            Call: self._eval_call_expr,
            Index: self._eval_index_expr,
            MethodCall: self._eval_method_expr,
        }

    def _raise(self, msg):
        if self.current_line:
            raise Exception(f"[{self.current_line}번 줄] {msg}")
        raise Exception(msg)

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
        return self.type_name_of(value) or "없음"

    def is_hanco_value(self, value):
        if value is None:
            return True
        if isinstance(value, bool):
            return True
        if isinstance(value, (int, float, str)):
            return True
        if isinstance(value, list):
            return all(self.is_hanco_value(item) for item in value)
        return False

    def ensure_type(self, expected_type, value, var_name):
        if expected_type == TYPE_ANY:
            return
        actual_type = self.type_name_of(value)
        if actual_type != expected_type:
            self._raise(
                f"변수 '{var_name}'에는 {expected_type} 자료형만 저장할 수 있습니다. "
                f"(전달된 값의 자료형: {actual_type})"
            )

    def coerce_value(self, expected_type, value, var_name):
        if expected_type in {TYPE_ANY, None}:
            return value
        if self.type_name_of(value) == expected_type:
            return value
        if expected_type == TYPE_STRING:
            return str(value)
        if expected_type == TYPE_INT and isinstance(value, str):
            try:
                return int(value.strip())
            except ValueError:
                self._raise(f"입력값을 숫자로 변환할 수 없습니다. (변수: '{var_name}', 값: {value!r})")
        if expected_type == TYPE_FLOAT and isinstance(value, str):
            try:
                return float(value.strip())
            except ValueError:
                self._raise(f"입력값을 실수로 변환할 수 없습니다. (변수: '{var_name}', 값: {value!r})")
        if expected_type == TYPE_BOOL and isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {BOOL_TRUE, "true", "1", "yes", "y"}:
                return True
            if normalized in {BOOL_FALSE, "false", "0", "no", "n"}:
                return False
            self._raise(f"입력값을 참거짓으로 변환할 수 없습니다. (변수: '{var_name}', 값: {value!r})")
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
                except ValueError:
                    self._raise(f"값을 숫자로 변환할 수 없습니다. (값: {value!r})")
        if type_name == TYPE_FLOAT:
            if isinstance(value, bool):
                return float(value)
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                try:
                    return float(value.strip())
                except ValueError:
                    self._raise(f"값을 실수로 변환할 수 없습니다. (값: {value!r})")
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
                self._raise(f"값을 참거짓으로 변환할 수 없습니다. (값: {value!r})")
        self._raise(f"지원하지 않는 자료형 변환입니다. ({type_name})")

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
        self._raise(f"선언하지 않은 변수 '{name}'를 사용했습니다.")

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
        self._raise(f"선언하지 않은 변수 '{name}'에 값을 대입할 수 없습니다.")

    def declare_var(self, name, type_name, value):
        value = self.coerce_value(type_name, value, name)
        self.ensure_type(type_name, value, name)
        self.current_vars()[name] = value
        self.current_var_types()[name] = type_name
        return value

    def import_stdlib(self, name):
        if name not in STANDARD_LIBRARIES:
            self._raise(f"표준 라이브러리 '{name}'를 찾을 수 없습니다.")
        namespace = StdNamespace(name, STANDARD_LIBRARIES[name])
        self.current_vars()[name] = namespace
        self.current_var_types()[name] = TYPE_ANY
        return namespace

    # --- Private node handlers ---

    def _exec_function(self, node):
        self.functions[node.name] = node
        return None

    def _exec_return(self, node):
        raise ReturnSignal(self.eval_expr(node.value))

    def _exec_break(self, node):
        raise BreakSignal()

    def _exec_continue(self, node):
        raise ContinueSignal()

    def _exec_use(self, node):
        result = None
        for name in node.names:
            result = self.import_stdlib(name)
        return result

    def _exec_try(self, node):
        try:
            try:
                return self.eval_block(node.try_body)
            except (ReturnSignal, BreakSignal, ContinueSignal):
                raise
            except Exception as exc:
                if node.catch_body is None:
                    raise
                return self.eval_catch(node.error_name, exc, node.catch_body)
        finally:
            if node.finally_body is not None:
                self.eval_block(node.finally_body)

    def eval_catch(self, error_name, error, body):
        vars_dict = self.current_vars()
        var_types = self.current_var_types()
        had_value = error_name in vars_dict
        had_type = error_name in var_types
        old_value = vars_dict.get(error_name)
        old_type = var_types.get(error_name)

        vars_dict[error_name] = str(error)
        var_types[error_name] = TYPE_STRING

        try:
            return self.eval_block(body)
        finally:
            if had_value:
                vars_dict[error_name] = old_value
            else:
                vars_dict.pop(error_name, None)

            if had_type:
                var_types[error_name] = old_type
            else:
                var_types.pop(error_name, None)

    def _exec_list_decl(self, node):
        items = [self.eval_expr(item) for item in node.items]
        return self.declare_var(node.name, TYPE_LIST, items)

    def _exec_var_decl(self, node):
        value = self.eval_expr(node.value)
        return self.declare_var(node.name, node.type_name, value)

    def _exec_assign(self, node):
        value = self.eval_expr(node.value)
        return self.assign_var(node.name, value)

    def _exec_index_assign(self, node):
        target = self.eval_expr(node.target)
        index = self.eval_expr(node.index)
        value = self.eval_expr(node.value)
        self.assign_index(target, index, value)
        return value

    def _exec_call_node(self, node):
        return self.eval_call(node.name, node.args)

    # --- Private expr handlers ---

    def _eval_literal(self, node):
        return node.value

    def _eval_var(self, node):
        return self.resolve_var(node.name)

    def _eval_call_expr(self, node):
        return self.eval_call(node.name, node.args)

    def _eval_index_expr(self, node):
        target = self.eval_expr(node.target)
        index = self.eval_expr(node.index)
        return self.read_index(target, index)

    def _eval_method_expr(self, node):
        target = self.eval_expr(node.target)
        args = [self.eval_expr(arg) for arg in node.args]
        return self.eval_method_call(target, node.method, args)

    # --- Core evaluation ---

    def run(self, ast):
        return self.eval_node(ast)

    def eval_node(self, node):
        if node.line:
            self.current_line = node.line
        handler = self._node_dispatch.get(type(node))
        if handler:
            return handler(node)
        return self.eval_expr(node)

    def eval_program(self, program):
        result = None
        for statement in program.statements:
            result = self.eval_node(statement)
        return result

    def eval_block(self, statements):
        result = None
        for statement in statements:
            result = self.eval_node(statement)
        return result

    def eval_if(self, node):
        for condition, body in node.branches:
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

        if not isinstance(start, int) or not isinstance(end, int):
            self._raise("반복문의 범위는 정수여야 합니다.")

        step = 1 if start <= end else -1

        if self.resolve_var_type(node.var_name) is None:
            self.declare_var(node.var_name, TYPE_INT, start)
        else:
            self.assign_var(node.var_name, start)

        vars_dict = self.current_vars()
        var_name = node.var_name
        current = start

        result = None
        while True:
            if step == 1 and current > end:
                break
            if step == -1 and current < end:
                break

            vars_dict[var_name] = current

            try:
                result = self.eval_block(node.body)
            except ContinueSignal:
                pass
            except BreakSignal:
                break

            current = vars_dict[var_name] + step

        return result

    def eval_expr(self, node):
        if node.line:
            self.current_line = node.line
        handler = self._expr_dispatch.get(type(node))
        if handler:
            return handler(node)
        self._raise(f"지원하지 않는 AST 노드입니다. ({type(node).__name__})")

    def eval_binary(self, node):
        left = self.eval_expr(node.left)
        right = self.eval_expr(node.right)
        op = node.op

        if op == "<": return left < right
        if op == ">": return left > right
        if op == "<=": return left <= right
        if op == ">=": return left >= right
        if op == LOGIC_AND: return bool(left) and bool(right)
        if op == LOGIC_OR: return bool(left) or bool(right)
        if op == "==": return left == right
        if op == "!=": return left != right

        if op == "+" and (isinstance(left, str) or isinstance(right, str)):
            return self.stringify_value(left) + self.stringify_value(right)

        if op == "*" and isinstance(left, str) and isinstance(right, int) and not isinstance(right, bool):
            return left * right
        if op == "*" and isinstance(right, str) and isinstance(left, int) and not isinstance(left, bool):
            return right * left

        if op in ("+", "-", "*", "/", "%"):
            if not isinstance(left, (int, float)) or isinstance(left, bool):
                self._raise(
                    f"'{op}' 연산자는 숫자에만 사용할 수 있습니다. "
                    f"(왼쪽 값의 자료형: {self.type_label_of(left)})"
                )
            if not isinstance(right, (int, float)) or isinstance(right, bool):
                self._raise(
                    f"'{op}' 연산자는 숫자에만 사용할 수 있습니다. "
                    f"(오른쪽 값의 자료형: {self.type_label_of(right)})"
                )
            if op in ("/", "%") and right == 0:
                self._raise("0으로 나눌 수 없습니다.")
            if op == "+": return left + right
            if op == "-": return left - right
            if op == "*": return left * right
            if op == "/": return left / right
            if op == "%": return left % right

        self._raise(f"지원하지 않는 연산자입니다. ({op})")

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
                self._raise("길이 함수는 인자를 1개만 받습니다.")
            value = args[0]
            if not isinstance(value, (str, list)):
                self._raise(
                    f"길이 함수는 문자열 또는 목록에만 사용할 수 있습니다. "
                    f"(전달된 값의 자료형: {self.type_label_of(value)})"
                )
            return len(value)

        if name == BUILTIN_TYPE_OF:
            if len(args) != 1:
                self._raise("자료형 함수는 인자를 1개만 받습니다.")
            return self.type_label_of(args[0])

        if name == BUILTIN_EXISTS:
            if len(args) != 1:
                self._raise("있는가 함수는 인자를 1개만 받습니다.")
            return args[0] is not None

        if name == BUILTIN_MISSING:
            if len(args) != 1:
                self._raise("없는가 함수는 인자를 1개만 받습니다.")
            return args[0] is None

        if name == BUILTIN_IS_NUMBER:
            if len(args) != 1:
                self._raise("숫자인가 함수는 인자를 1개만 받습니다.")
            return isinstance(args[0], (int, float)) and not isinstance(args[0], bool)

        if name == BUILTIN_IS_INTEGER:
            if len(args) != 1:
                self._raise("정수인가 함수는 인자를 1개만 받습니다.")
            return isinstance(args[0], int) and not isinstance(args[0], bool)

        target_type = TYPE_ALIASES.get(name, name)
        if target_type in {TYPE_STRING, TYPE_INT, TYPE_FLOAT, TYPE_BOOL}:
            if len(args) != 1:
                self._raise(f"자료형 변환 함수 '{name}'는 인자를 1개만 받습니다.")
            return self.convert_value(target_type, args[0])

        if name not in self.functions:
            self._raise(f"정의되지 않은 함수 '{name}'를 호출했습니다.")

        func = self.functions[name]
        if len(args) != len(func.params):
            self._raise(
                f"함수 '{name}' 호출 시 인자 수가 맞지 않습니다. "
                f"(필요: {len(func.params)}개, 전달: {len(args)}개)"
            )

        frame = {
            "vars": dict(zip(func.params, args)),
            "var_types": {param: TYPE_ANY for param in func.params},
            "name": name,
        }
        self.frames.append(frame)
        try:
            self.eval_block(func.body)
        except ReturnSignal as signal:
            return signal.value
        finally:
            self.frames.pop()
        return None

    def eval_method_call(self, target, method, args):
        if isinstance(target, StdNamespace):
            payload = {"기능": method, "인자": args}
            try:
                value = target.handler(payload)
            except Exception as exc:
                msg = str(exc)
                if self.current_line and not msg.startswith("["):
                    raise Exception(f"[{self.current_line}번 줄] {msg}") from None
                raise
            except BaseException:
                self._raise(f"표준 라이브러리 '{target.name}' 호출 중 알 수 없는 오류가 발생했습니다.")

            if not self.is_hanco_value(value):
                self._raise(f"표준 라이브러리 '{target.name}'는 한코 자료형만 반환해야 합니다.")
            return value

        if method == METHOD_SLICE:
            if len(args) != 2:
                self._raise("자르기는 시작과 끝 인자 2개를 받아야 합니다.")
            start, end = args
            if not isinstance(start, int) or not isinstance(end, int):
                self._raise("자르기의 범위는 정수여야 합니다.")
            if isinstance(target, (list, str)):
                return target[start:end + 1]
            self._raise(
                f"자르기는 문자열 또는 목록에만 사용할 수 있습니다. "
                f"(자료형: {self.type_label_of(target)})"
            )

        if isinstance(target, list):
            method = LIST_METHOD_ALIASES.get(method, method)

            if method == METHOD_APPEND:
                if len(args) != 1:
                    self._raise("목록:추가는 인자를 1개만 받습니다.")
                target.append(args[0])
                return target

            if method == METHOD_REMOVE:
                if len(args) == 0:
                    if not target:
                        self._raise("빈 목록에서는 제거할 수 없습니다.")
                    return target.pop()
                if len(args) == 1:
                    index = args[0]
                    if not isinstance(index, int):
                        self._raise("목록:제거의 인덱스는 정수여야 합니다.")
                    if index < 0 or index >= len(target):
                        self._raise(
                            f"목록 인덱스 범위를 벗어났습니다. "
                            f"(인덱스: {index}, 목록 크기: {len(target)})"
                        )
                    return target.pop(index)
                self._raise("목록:제거는 인자를 0개 또는 1개만 받습니다.")

            self._raise(f"목록에 '{method}' 함수가 없습니다.")

        if isinstance(target, str):
            method = STRING_METHOD_ALIASES.get(method, method)

            if method == METHOD_CONTAINS:
                if len(args) != 1:
                    self._raise("문자열:포함은 인자를 1개만 받습니다.")
                return self.stringify_value(args[0]) in target

            if method == METHOD_STRIP:
                if args:
                    self._raise("문자열:제거앞뒤공백은 인자를 받지 않습니다.")
                return target.strip()

            if method == METHOD_SPLIT:
                if len(args) != 1:
                    self._raise("문자열:나누기는 인자를 1개만 받습니다.")
                return target.split(self.stringify_value(args[0]))

            self._raise(f"문자열에 '{method}' 함수가 없습니다.")

        self._raise(f"자료형 '{self.type_label_of(target)}'에는 '{method}' 함수가 없습니다.")

    def read_index(self, target, index):
        if not isinstance(target, (list, str)):
            self._raise(
                f"인덱싱은 목록 또는 문자열에만 사용할 수 있습니다. "
                f"(자료형: {self.type_label_of(target)})"
            )
        if not isinstance(index, int):
            self._raise(f"인덱스는 정수여야 합니다. (전달된 자료형: {self.type_label_of(index)})")
        if index < 0 or index >= len(target):
            self._raise(f"인덱스 범위를 벗어났습니다. (인덱스: {index}, 크기: {len(target)})")
        return target[index]

    def assign_index(self, target, index, value):
        if isinstance(target, str):
            self._raise("문자열은 인덱스로 값을 바꿀 수 없습니다.")
        if not isinstance(target, list):
            self._raise(
                f"인덱스 대입은 목록에만 사용할 수 있습니다. "
                f"(자료형: {self.type_label_of(target)})"
            )
        if not isinstance(index, int):
            self._raise(f"인덱스는 정수여야 합니다. (전달된 자료형: {self.type_label_of(index)})")
        if index < 0 or index >= len(target):
            self._raise(f"인덱스 범위를 벗어났습니다. (인덱스: {index}, 크기: {len(target)})")
        target[index] = value

    def truthy(self, value):
        return bool(value)
