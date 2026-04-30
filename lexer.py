import re

KEYWORDS = {"함수","인수","반환","조건","아니면","변수","목록","그리고","또는","반복","멈춤","건너뛰기"}

class Token:
    def __init__(self,t,v,line):
        self.type=t
        self.value=v
        self.line=line


class Lexer:
    def __init__(self,code):
        self.code=code

    def tokenize(self):
        patterns = [
            ("BLOCK_COMMENT", r'::\[(?:.|\n)*?\]::'),
            ("COMMENT", r'::[^\n]*'),
            ("FLOAT", r'\d+\.\d+'),
            ("NUMBER", r'\d+'),
            ("STRING", r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\''),
            ("IDENT", r'[가-힣a-zA-Z_][가-힣a-zA-Z0-9_]*'),
            ("OP", r'==|!=|<=|>=|<|>|\+|\-|\*|/|%'),
            ("SYMBOL", r'[(),<>\[\]=~:]'),
            ("NEWLINE", r'\n+'),
            ("SKIP", r'[ \t]+'),
        ]

        master = re.compile("|".join(f"(?P<{n}>{p})" for n,p in patterns))

        tokens=[]
        line_num = 1

        for m in master.finditer(self.code):
            text = m.group()
            k = m.lastgroup
            v = text
            current_line = line_num

            if k == "BLOCK_COMMENT":
                line_num += text.count("\n")
                continue

            if k == "COMMENT":
                continue

            if k == "NEWLINE":
                line_num += text.count("\n")
                tokens.append(Token("NEWLINE", "\\n", current_line))
                continue

            if k == "SKIP":
                continue

            if k=="FLOAT":
                tokens.append(Token("FLOAT",v,current_line))

            elif k=="NUMBER":
                tokens.append(Token("NUMBER",v,current_line))

            elif k=="STRING":
                tokens.append(Token("STRING",v,current_line))

            elif k=="IDENT":
                if v in KEYWORDS:
                    tokens.append(Token("KEYWORD",v,current_line))
                elif v in {"참", "거짓"}:
                    tokens.append(Token("BOOL",v,current_line))
                else:
                    tokens.append(Token("IDENT",v,current_line))

            elif k=="OP":
                tokens.append(Token("OP",v,current_line))

            elif k=="SYMBOL":
                tokens.append(Token("SYMBOL",v,current_line))

        return tokens
