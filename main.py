from hanco.core.lexer import Lexer
from hanco.core.parser import Parser
from hanco.core.vm import VM

code = """
출력("안녕!")
"""

lexer = Lexer(code)
tokens = lexer.tokenize()

parser = Parser(tokens)
ast = parser.parse()

print("\n=== 실행 결과 ===")
vm = VM()
vm.run(ast)
