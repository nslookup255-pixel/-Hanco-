from hanco.core.lexer import Lexer
from hanco.core.parser import Parser
from hanco.core.vm import VM


def execute(code: str):

    tokens = Lexer(code).tokenize()

    ast = Parser(tokens).parse()

    vm = VM()

    vm.run(ast)