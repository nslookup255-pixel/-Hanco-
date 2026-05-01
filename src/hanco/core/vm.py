class VM:
    def __init__(self,code):
        self.code=code
        self.pc=0
        self.stack=[]
        self.call=[]
        self.frame={
            "vars": {},
            "var_types": {},
            "stack_base": 0,
            "name": "<main>",
        }
        self.labels={}
        self.funcs={}

        # 출력 콜백: GUI 환경에서 콘솔 패널로 교체 가능
        # 기본값은 터미널 print()
        self.output_handler = print

        # 입력 콜백: GUI 환경에서 인라인 입력창으로 교체 가능
        # 기본값은 터미널 input()
        self.input_handler = input

        for i,(o,a) in enumerate(code):
            if o=="LABEL": self.labels[a]=i
            if o=="FUNC":
                name, params = a
                self.funcs[name] = {
                    "pc": i + 1,
                    "params": params,
                }

    def format_value(self,v):
        if isinstance(v,list):
            return "(" + ", ".join(str(self.format_value(x)) for x in v) + ")"
        if isinstance(v,bool):
            return "참" if v else "거짓"
        return v

    def stringify_value(self, value):
        return str(self.format_value(value))

    def type_name_of(self, value):
        if isinstance(value, bool):
            return "참거짓"
        if isinstance(value, int):
            return "숫자"
        if isinstance(value, float):
            return "실수"
        if isinstance(value, str):
            return "문자"
        if isinstance(value, list):
            return "목록"
        return None

    def ensure_type(self, expected_type, value, var_name):
        if expected_type == "-":
            return

        actual_type = self.type_name_of(value)
        if actual_type != expected_type:
            raise Exception(
                f"변수 '{var_name}'에는 {expected_type} 자료형만 저장할 수 있습니다. "
                f"(현재 값: {actual_type})"
            )

    def coerce_value(self, expected_type, value, var_name):
        if expected_type == "-" or expected_type is None:
            return value

        if self.type_name_of(value) == expected_type:
            return value

        if expected_type == "문자":
            return str(value)

        if expected_type == "숫자":
            if isinstance(value, str):
                try:
                    return int(value.strip())
                except ValueError as exc:
                    raise Exception(
                        f"입력값을 숫자로 변환할 수 없습니다. (변수: {var_name}, 값: {value})"
                    ) from exc

        if expected_type == "실수":
            if isinstance(value, str):
                try:
                    return float(value.strip())
                except ValueError as exc:
                    raise Exception(
                        f"입력값을 실수로 변환할 수 없습니다. (변수: {var_name}, 값: {value})"
                    ) from exc

        if expected_type == "참거짓":
            if isinstance(value, str):
                normalized = value.strip().lower()
                if normalized in {"참", "true", "1", "yes", "y"}:
                    return True
                if normalized in {"거짓", "false", "0", "no", "n"}:
                    return False
                raise Exception(
                    f"입력값을 참거짓으로 변환할 수 없습니다. (변수: {var_name}, 값: {value})"
                )

        self.ensure_type(expected_type, value, var_name)
        return value

    def convert_value(self, type_name, value):
        if type_name == "문자":
            return self.stringify_value(value)

        if type_name == "숫자":
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

        if type_name == "실수":
            if isinstance(value, bool):
                return float(value)
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                try:
                    return float(value.strip())
                except ValueError as exc:
                    raise Exception(f"값을 실수로 변환할 수 없습니다. (값: {value})") from exc

        if type_name == "참거짓":
            if isinstance(value, bool):
                return value
            if isinstance(value, (int, float)):
                return bool(value)
            if isinstance(value, str):
                normalized = value.strip().lower()
                if normalized in {"참", "true", "1", "yes", "y"}:
                    return True
                if normalized in {"거짓", "false", "0", "no", "n", ""}:
                    return False
                raise Exception(f"값을 참거짓으로 변환할 수 없습니다. (값: {value})")

        raise Exception(f"지원하지 않는 자료형 변환입니다. ({type_name})")

    def current_vars(self):
        return self.frame["vars"]

    def current_var_types(self):
        return self.frame["var_types"]

    def run(self):
        while self.pc<len(self.code):
            op,arg=self.code[self.pc]

            if op=="PUSH":
                self.stack.append(arg)

            elif op=="LOAD":
                if arg not in self.current_vars():
                    raise Exception(f"선언되지 않은 변수 '{arg}' 를 읽을 수 없습니다.")
                self.stack.append(self.current_vars()[arg])

            elif op=="STORE":
                self.current_vars()[arg]=self.stack.pop()
                self.current_var_types().setdefault(arg, "-")

            elif op=="DECLARE":
                name, type_name = arg
                value = self.stack.pop()
                value = self.coerce_value(type_name, value, name)
                self.ensure_type(type_name, value, name)
                self.current_vars()[name] = value
                self.current_var_types()[name] = type_name

            elif op=="ASSIGN":
                value = self.stack.pop()
                if arg not in self.current_var_types():
                    raise Exception(f"선언되지 않은 변수 '{arg}' 에 값을 대입할 수 없습니다.")
                value = self.coerce_value(self.current_var_types()[arg], value, arg)
                self.ensure_type(self.current_var_types()[arg], value, arg)
                self.current_vars()[arg] = value

            elif op=="MAKE_LIST":
                items=[self.stack.pop() for _ in range(arg)][::-1]
                self.stack.append(items)

            elif op=="INDEX":
                index = self.stack.pop()
                target = self.stack.pop()

                if not isinstance(target, list):
                    raise Exception("리스트가 아닌 값에는 인덱싱을 사용할 수 없습니다.")
                if not isinstance(index, int):
                    raise Exception("리스트 인덱스는 숫자여야 합니다.")
                if index < 0 or index >= len(target):
                    raise Exception(f"리스트 인덱스 범위를 벗어났습니다. (인덱스: {index})")

                self.stack.append(target[index])

            elif op=="INDEX_ASSIGN":
                value = self.stack.pop()
                index = self.stack.pop()
                target = self.stack.pop()

                if not isinstance(target, list):
                    raise Exception("리스트가 아닌 값에는 인덱싱 대입을 사용할 수 없습니다.")
                if not isinstance(index, int):
                    raise Exception("리스트 인덱스는 숫자여야 합니다.")
                if index < 0 or index >= len(target):
                    raise Exception(f"리스트 인덱스 범위를 벗어났습니다. (인덱스: {index})")

                target[index] = value

            elif op=="METHOD_CALL":
                method, argc = arg
                args = [self.stack.pop() for _ in range(argc)][::-1]
                target = self.stack.pop()

                if method == "자르기":
                    if argc != 2:
                        raise Exception("자르기 함수는 시작과 끝 인자를 받아야 합니다.")
                    start, end = args
                    if not isinstance(start, int) or not isinstance(end, int):
                        raise Exception("자르기 범위는 숫자여야 합니다.")
                    if isinstance(target, (list, str)):
                        self.stack.append(target[start:end])
                    else:
                        raise Exception("자르기 함수는 문자열 또는 리스트에만 사용할 수 있습니다.")

                elif isinstance(target, list):
                    if method == "추가":
                        if argc != 1:
                            raise Exception("목록 추가 함수는 인자를 1개 받아야 합니다.")
                        target.append(args[0])
                        self.stack.append(target)

                    elif method == "삭제":
                        if argc == 0:
                            if not target:
                                raise Exception("빈 리스트에서는 삭제할 수 없습니다.")
                            self.stack.append(target.pop())
                        elif argc == 1:
                            index = args[0]
                            if not isinstance(index, int):
                                raise Exception("목록 삭제 인덱스는 숫자여야 합니다.")
                            if index < 0 or index >= len(target):
                                raise Exception(f"리스트 인덱스 범위를 벗어났습니다. (인덱스: {index})")
                            self.stack.append(target.pop(index))
                        else:
                            raise Exception("목록 삭제 함수는 인자를 0개 또는 1개만 받습니다.")

                    else:
                        raise Exception(f"지원하지 않는 목록 함수입니다. ({method})")

                elif isinstance(target, str):
                    if method == "포함":
                        if argc != 1:
                            raise Exception("문자열 포함 함수는 인자를 1개 받아야 합니다.")
                        self.stack.append(self.stringify_value(args[0]) in target)

                    elif method == "제거":
                        if argc != 0:
                            raise Exception("문자열 제거 함수는 인자를 받지 않습니다.")
                        self.stack.append(target.strip())

                    elif method == "나누기":
                        if argc != 1:
                            raise Exception("문자열 나누기 함수는 인자를 1개 받아야 합니다.")
                        self.stack.append(target.split(self.stringify_value(args[0])))

                    else:
                        raise Exception(f"지원하지 않는 문자열 함수입니다. ({method})")

                else:
                    raise Exception(f"지원하지 않는 메서드 호출입니다. ({method})")

            elif op in ["+","-","*","/","%","==","!=","<",">","<=",">="]:
                b=self.stack.pop()
                a=self.stack.pop()
                if op == "+" and (isinstance(a, str) or isinstance(b, str)):
                    self.stack.append(self.stringify_value(a) + self.stringify_value(b))
                else:
                    self.stack.append(eval(f"a {op} b"))

            elif op=="그리고":
                b=self.stack.pop()
                a=self.stack.pop()
                self.stack.append(bool(a) and bool(b))

            elif op=="또는":
                b=self.stack.pop()
                a=self.stack.pop()
                self.stack.append(bool(a) or bool(b))


            elif op=="CALL":
                name, argc = arg

                if name=="출력":
                    values = [self.stack.pop() for _ in range(argc)][::-1]
                    print(" ".join(str(self.format_value(value)) for value in values))
                    self.pc+=1
                    continue

                if name=="입력":
                    values = [self.stack.pop() for _ in range(argc)][::-1]
                    prompt = " ".join(str(self.format_value(value)) for value in values)
                    self.stack.append(input(prompt))
                    self.pc+=1
                    continue

                if name=="길이":
                    if argc != 1:
                        raise Exception("길이 함수는 인자를 1개만 받습니다.")
                    value = self.stack.pop()
                    if not isinstance(value, (str, list)):
                        raise Exception("길이 함수는 문자열 또는 리스트에만 사용할 수 있습니다.")
                    self.stack.append(len(value))
                    self.pc += 1
                    continue

                if name in {"문자", "숫자", "실수", "참거짓"}:
                    if argc != 1:
                        raise Exception(f"자료형 변환 함수 '{name}' 는 인자를 1개만 받습니다.")
                    value = self.stack.pop()
                    self.stack.append(self.convert_value(name, value))
                    self.pc += 1
                    continue

                if name not in self.funcs:
                    raise Exception(f"정의되지 않은 함수 '{name}' 입니다.")

                func_info = self.funcs[name]
                expected_argc = len(func_info["params"])
                if argc != expected_argc:
                    raise Exception(
                        f"함수 '{name}' 호출 인자 수가 맞지 않습니다. "
                        f"(필요: {expected_argc}, 전달: {argc})"
                    )

                self.call.append((self.pc, self.frame))
                self.frame = {
                    "vars": {},
                    "var_types": {},
                    "stack_base": len(self.stack) - argc,
                    "name": name,
                }
                self.pc=func_info["pc"]
                continue

            elif op=="RET":
                return_value = None
                if len(self.stack) > self.frame["stack_base"]:
                    return_value = self.stack.pop()

                while len(self.stack) > self.frame["stack_base"]:
                    self.stack.pop()

                if not self.call:
                    if return_value is not None:
                        self.stack.append(return_value)
                    return
                self.pc,self.frame=self.call.pop()
                if return_value is not None:
                    self.stack.append(return_value)

            elif op=="JMP":
                self.pc=self.labels[arg]
                continue

            elif op=="JMP_IF_FALSE":
                if not self.stack.pop():
                    self.pc=self.labels[arg]
                    continue

            self.pc+=1
    def step(self):
        """
        명령어 한 개를 실행합니다.
        계속 실행 가능하면 True, 종료(코드 끝 or RET)면 False 를 반환합니다.
        """
        if self.pc >= len(self.code):
            return False

        op, arg = self.code[self.pc]

        # JMP 계열은 내부에서 pc 를 직접 갱신 후 return 하므로
        # 여기서 미리 +1 하지 않습니다.
        advanced = self._exec(op, arg)

        if advanced is None:    # 일반 명령: pc 를 1 전진
            self.pc += 1
        # advanced == "jumped" 인 경우 _exec 내부에서 이미 pc 설정 완료

        return self.pc <= len(self.code)  # 끝 이후면 False

    # ── 내부 실행 엔진 ─────────────────────────────────────────────────────

    def _exec(self, op: str, arg) -> str | None:
        """
        명령어(op, arg) 한 개를 실행합니다.

        Returns:
            None     — 호출자가 pc += 1 을 처리해야 합니다.
            "jumped" — 이미 pc 가 갱신됐습니다 (JMP, CALL, RET 등).
        """
        if op == "PUSH":
            self.stack.append(arg)

        elif op == "LOAD":
            if arg not in self.current_vars():
                raise Exception(f"선언되지 않은 변수 '{arg}' 를 읽을 수 없습니다.")
            self.stack.append(self.current_vars()[arg])

        elif op == "STORE":
            self.current_vars()[arg] = self.stack.pop()
            self.current_var_types().setdefault(arg, "-")

        elif op == "DECLARE":
            name, type_name = arg
            value = self.stack.pop()
            value = self.coerce_value(type_name, value, name)
            self.ensure_type(type_name, value, name)
            self.current_vars()[name] = value
            self.current_var_types()[name] = type_name

        elif op == "ASSIGN":
            value = self.stack.pop()
            if arg not in self.current_var_types():
                raise Exception(f"선언되지 않은 변수 '{arg}' 에 값을 대입할 수 없습니다.")
            value = self.coerce_value(self.current_var_types()[arg], value, arg)
            self.ensure_type(self.current_var_types()[arg], value, arg)
            self.current_vars()[arg] = value

        elif op == "MAKE_LIST":
            items = [self.stack.pop() for _ in range(arg)][::-1]
            self.stack.append(items)

        elif op == "INDEX":
            index  = self.stack.pop()
            target = self.stack.pop()
            if not isinstance(target, list):
                raise Exception("리스트가 아닌 값에는 인덱싱을 사용할 수 없습니다.")
            if not isinstance(index, int):
                raise Exception("리스트 인덱스는 숫자여야 합니다.")
            if index < 0 or index >= len(target):
                raise Exception(f"리스트 인덱스 범위를 벗어났습니다. (인덱스: {index})")
            self.stack.append(target[index])

        elif op == "INDEX_ASSIGN":
            value  = self.stack.pop()
            index  = self.stack.pop()
            target = self.stack.pop()
            if not isinstance(target, list):
                raise Exception("리스트가 아닌 값에는 인덱싱 대입을 사용할 수 없습니다.")
            if not isinstance(index, int):
                raise Exception("리스트 인덱스는 숫자여야 합니다.")
            if index < 0 or index >= len(target):
                raise Exception(f"리스트 인덱스 범위를 벗어났습니다. (인덱스: {index})")
            target[index] = value

        elif op == "METHOD_CALL":
            method, argc = arg
            args   = [self.stack.pop() for _ in range(argc)][::-1]
            target = self.stack.pop()

            if method == "자르기":
                if argc != 2:
                    raise Exception("자르기 함수는 시작과 끝 인자를 받아야 합니다.")
                start, end = args
                if not isinstance(start, int) or not isinstance(end, int):
                    raise Exception("자르기 범위는 숫자여야 합니다.")
                if isinstance(target, (list, str)):
                    self.stack.append(target[start:end])
                else:
                    raise Exception("자르기 함수는 문자열 또는 리스트에만 사용할 수 있습니다.")

            elif isinstance(target, list):
                if method == "추가":
                    if argc != 1:
                        raise Exception("목록 추가 함수는 인자를 1개 받아야 합니다.")
                    target.append(args[0])
                    self.stack.append(target)
                elif method == "삭제":
                    if argc == 0:
                        if not target:
                            raise Exception("빈 리스트에서는 삭제할 수 없습니다.")
                        self.stack.append(target.pop())
                    elif argc == 1:
                        index = args[0]
                        if not isinstance(index, int):
                            raise Exception("목록 삭제 인덱스는 숫자여야 합니다.")
                        if index < 0 or index >= len(target):
                            raise Exception(f"리스트 인덱스 범위를 벗어났습니다. (인덱스: {index})")
                        self.stack.append(target.pop(index))
                    else:
                        raise Exception("목록 삭제 함수는 인자를 0개 또는 1개만 받습니다.")
                else:
                    raise Exception(f"지원하지 않는 목록 함수입니다. ({method})")

            elif isinstance(target, str):
                if method == "포함":
                    if argc != 1:
                        raise Exception("문자열 포함 함수는 인자를 1개 받아야 합니다.")
                    self.stack.append(self.stringify_value(args[0]) in target)
                elif method == "제거":
                    if argc != 0:
                        raise Exception("문자열 제거 함수는 인자를 받지 않습니다.")
                    self.stack.append(target.strip())
                elif method == "나누기":
                    if argc != 1:
                        raise Exception("문자열 나누기 함수는 인자를 1개 받아야 합니다.")
                    self.stack.append(target.split(self.stringify_value(args[0])))
                else:
                    raise Exception(f"지원하지 않는 문자열 함수입니다. ({method})")
            else:
                raise Exception(f"지원하지 않는 메서드 호출입니다. ({method})")

        elif op in ["+", "-", "*", "/", "%", "==", "!=", "<", ">", "<=", ">="]:
            b = self.stack.pop()
            a = self.stack.pop()
            if op == "+" and (isinstance(a, str) or isinstance(b, str)):
                self.stack.append(self.stringify_value(a) + self.stringify_value(b))
            else:
                self.stack.append(eval(f"a {op} b"))

        elif op == "그리고":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(bool(a) and bool(b))

        elif op == "또는":
            b = self.stack.pop()
            a = self.stack.pop()
            self.stack.append(bool(a) or bool(b))

        elif op == "CALL":
            name, argc = arg

            if name == "출력":
                values = [self.stack.pop() for _ in range(argc)][::-1]
                self.output_handler(" ".join(str(self.format_value(v)) for v in values))
                self.pc += 1
                return "jumped"

            if name == "입력":
                values = [self.stack.pop() for _ in range(argc)][::-1]
                prompt = " ".join(str(self.format_value(v)) for v in values)
                self.stack.append(self.input_handler(prompt))
                self.pc += 1
                return "jumped"

            if name == "길이":
                if argc != 1:
                    raise Exception("길이 함수는 인자를 1개만 받습니다.")
                value = self.stack.pop()
                if not isinstance(value, (str, list)):
                    raise Exception("길이 함수는 문자열 또는 리스트에만 사용할 수 있습니다.")
                self.stack.append(len(value))
                self.pc += 1
                return "jumped"

            if name in {"문자", "숫자", "실수", "참거짓"}:
                if argc != 1:
                    raise Exception(f"자료형 변환 함수 '{name}' 는 인자를 1개만 받습니다.")
                value = self.stack.pop()
                self.stack.append(self.convert_value(name, value))
                self.pc += 1
                return "jumped"

            if name not in self.funcs:
                raise Exception(f"정의되지 않은 함수 '{name}' 입니다.")

            func_info = self.funcs[name]
            expected_argc = len(func_info["params"])
            if argc != expected_argc:
                raise Exception(
                    f"함수 '{name}' 호출 인자 수가 맞지 않습니다. "
                    f"(필요: {expected_argc}, 전달: {argc})"
                )

            self.call.append((self.pc + 1, self.frame))
            self.frame = {
                "vars": {},
                "var_types": {},
                "stack_base": len(self.stack) - argc,
                "name": name,
            }
            self.pc = func_info["pc"]
            return "jumped"

        elif op == "RET":
            return_value = None
            if len(self.stack) > self.frame["stack_base"]:
                return_value = self.stack.pop()

            while len(self.stack) > self.frame["stack_base"]:
                self.stack.pop()

            if not self.call:
                if return_value is not None:
                    self.stack.append(return_value)
                self.pc = len(self.code)   # 종료 표시
                return "jumped"

            self.pc, self.frame = self.call.pop()
            if return_value is not None:
                self.stack.append(return_value)
            return "jumped"

        elif op == "JMP":
            self.pc = self.labels[arg]
            return "jumped"

        elif op == "JMP_IF_FALSE":
            if not self.stack.pop():
                self.pc = self.labels[arg]
            else:
                self.pc += 1
            return "jumped"

        elif op in ("LABEL", "FUNC"):
            pass   # 실행 시점에는 무시

        return None  # 호출자가 pc += 1 처리
