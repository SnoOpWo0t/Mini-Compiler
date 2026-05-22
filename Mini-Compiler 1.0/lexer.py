from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Token:
    type: str
    value: str
    line: int
    column: int


keywords = {'int', 'void', 'if', 'else', 'while', 'print', 'return'}

TOKEN_SPECIFICATION = [
    ('COMMENT',  r'//[^\n]*'),
    ('NUMBER',   r'\d+'),
    ('ID',       r'[A-Za-z_][A-Za-z0-9_]*'),
    ('REL',      r'==|!=|<=|>=|<|>'),
    ('OP',       r'[+\-*/]'),
    ('ASSIGN',   r'='),
    ('LPAREN',   r'\('),
    ('RPAREN',   r'\)'),
    ('LBRACE',   r'\{'),
    ('RBRACE',   r'\}'),
    ('COMMA',    r','),
    ('SEMICOLON',r';'),
    ('SKIP',     r'[ \t\r\f\v]+'),
    ('NEWLINE',  r'\n'),
    ('MISMATCH', r'.'),
]

TOK_REGEX = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_SPECIFICATION)


def lexer(code):
    tokens = []
    line = 1
    line_start = 0

    for mo in re.finditer(TOK_REGEX, code):
        kind = mo.lastgroup
        value = mo.group()
        column = mo.start() - line_start + 1

        if kind == 'NEWLINE':
            line += 1
            line_start = mo.end()
            continue

        if kind == 'COMMENT' or kind == 'SKIP':
            continue

        if kind == 'ID' and value in keywords:
            kind = 'KEYWORD'

        if kind == 'MISMATCH':
            raise RuntimeError(f'Unexpected character {value!r} at line {line}, column {column}')

        tokens.append(Token(kind, value, line, column))

    tokens.append(Token('EOF', '', line, 0))
    return tokens