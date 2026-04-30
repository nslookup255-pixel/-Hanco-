from lexer import Lexer
from parser import Parser
from compiler import Compiler
from vm import VM

code = """
출력<"안녕하세요!">
변수 문자 이름 = 입력<"이름을 입력하세요: ">
출력<"안녕하세요, " + 이름 + "!">
출력<"오늘 날씨는 어때요?">
변수 문자 날씨 = 입력<"날씨를 입력하세요: ">
출력<"날씨가 " + 날씨 + "군요!">
"""

lexer = Lexer(code)
tokens = lexer.tokenize()

parser = Parser(tokens)
ast = parser.parse()

compiler = Compiler()
compiler.compile(ast)

print("\n=== 실행 결과 ===")
vm = VM(compiler.get())
vm.run()
