from hanco.core.lexer import Lexer
from hanco.core.parser import Parser
from hanco.core.vm import VM

code = """
::새로 추가된 기능들
변수 숫자 정수값 = 12
변수 실수 실수값 = 3.5
변수 문자열 문자값 = "안녕하세요"
변수 자유 아무값 = 123
아무값 = "이제 자유 자료형입니다"

출력<자료형<정수값>>
출력<자료형<출력<"내부 출력">>>
출력<있는가<문자값>>
출력<없는가<출력<"없음 확인">>>
출력<숫자인가<실수값>>
출력<정수인가<정수값>>
출력<정수인가<실수값>>
출력<아무값>
"""

lexer = Lexer(code)
tokens = lexer.tokenize()

parser = Parser(tokens)
ast = parser.parse()

print("\n=== 실행 결과 ===")
vm = VM()
vm.run(ast)
