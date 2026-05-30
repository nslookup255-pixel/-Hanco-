from hanco.core.lexer import Lexer
from hanco.core.parser import Parser
from hanco.core.vm import VM

code = """
출력("안녕!")
시도<
    변수 숫자 하나 = "안녕"
~>
잡기 오류
    출력(오류)
~>
마지막
    출력("항상 실행")
~>
"""

lexer = Lexer(code)
tokens = lexer.tokenize()

parser = Parser(tokens)
ast = parser.parse()

print("\n=== 실행 결과 ===")
vm = VM()
vm.run(ast)
