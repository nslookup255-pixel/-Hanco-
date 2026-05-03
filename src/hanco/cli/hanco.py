import sys

from hanco.core.lexer import Lexer
from hanco.core.parser import Parser
from hanco.core.vm import VM
from importlib.metadata import version, PackageNotFoundError


try:
    ver = version("hanco")
except PackageNotFoundError:
    ver = "dev"

def run_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()

        tokens = Lexer(code).tokenize()
        ast = Parser(tokens).parse()

        vm = VM()
        vm.run(ast)

    except Exception as e:
        print(f"오류: {e}")


def repl():
    print(f"한코 REPL v{ver}")
    print("종료하려면 나가기 입력\n")

    vm = VM()

    while True:
        try:
            code = input(">>> ")

            if code.strip() in ["exit", "quit", "나가기"]:
                break

            tokens = Lexer(code).tokenize()
            ast = Parser(tokens).parse()

            vm.run(ast)

        except Exception as e:
            print(f"오류: {e}")


def main():
    args = sys.argv

    if len(args) == 1:
        print("사용법:")
        print("  hanco run <파일>")
        print("  hanco repl")
        print("  hanco version")
        return

    cmd = args[1]

    # hanco main.hanco 지원
    if cmd.endswith(".hanco"):
        run_file(cmd)
        return

    if cmd == "run":
        if len(args) < 3:
            print("파일을 입력하세요")
            return
        run_file(args[2])

    elif cmd == "repl":
        repl()

    elif cmd == "version":
        print(ver)
        
    else:
        print("알 수 없는 명령어")


if __name__ == "__main__":
    main()
