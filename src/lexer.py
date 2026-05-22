"""Lexer definitions for the Mini-Compiler using PLY.
 PLY (Python Lex-Yacc) library
Defines token regexes, reserved words, and helper utilities to run
the lexer and render token lists for debugging and output files.

Connections:
- Exports: `tokens` (list of token names used by PLY), `build_lexer()`,
    `tokenize_all()`, `render_tokens()` and the `token_log` used for
    inspection.
- Imported by: `parser.py` imports the `tokens` name at module import
    time (PLY requires the token list to be visible). `main.py` calls
    `tokenize_all()` and `render_tokens()` during Phase 1.
"""

import ply.lex as lex


# Mapping of reserved identifiers to token names.
#the word 'int' becomes token type 'INT'.
reserved = {
    "int":      "INT",
    "float":    "FLOAT",
    "void":     "VOID",
    "char":     "CHAR",
    "string":   "STR_TYPE",
    "if":       "IF",
    "else":     "ELSE",
    "while":    "WHILE",
    "for":      "FOR",
    "return":   "RETURN",
    "break":    "BREAK",
    "continue": "CONTINUE",
    "printf":   "PRINTF",
}

# Full token list PLY uses. Includes punctuation, operators and reserved names.
tokens = [
    "NUMBER", "FNUM", "STRING", "ID",
    "PLUS", "MINUS", "MUL", "DIV", "MOD",
    "ASSIGN",
    "EQ", "NE", "LE", "GE", "LT", "GT",
    "AND", "OR", "NOT",
    "LPAREN", "RPAREN", "LBRACE", "RBRACE",
    "LBRACKET", "RBRACKET",
    "SEMI", "COMMA",
] + list(set(reserved.values()))

#t_PLUS = r"\+" style lines — simple regex rules for single-character tokens.
t_PLUS   = r"\+"
t_MINUS  = r"-"
t_MUL    = r"\*"
t_DIV    = r"/"
t_MOD    = r"%"
t_EQ     = r"=="
t_NE     = r"!="
t_LE     = r"<="
t_GE     = r">="
t_LT     = r"<"
t_GT     = r">"
t_AND    = r"&&"
t_OR     = r"\|\|"
t_NOT    = r"!"
t_ASSIGN = r"="
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_SEMI   = r";"
t_COMMA  = r","
t_LBRACKET = r"\["
t_RBRACKET = r"\]"

t_ignore = " \t\r"


token_log = []          # list of dicts with idx, type, value, line, col


def t_COMMENT_BLOCK(t):
    r"/\*(.|\n)*?\*/"
    t.lexer.lineno += t.value.count("\n")


def t_COMMENT_LINE(t):
    r"//[^\n]*"
    pass


def t_FNUM(t):
    r"\d+\.\d+"
    t.value = float(t.value)
    return t


def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
    return t


def t_STRING(t):
    r'"([^"\\]|\\.)*"'
    return t


def t_ID(t):# matches identifiers and reserved words. If the value is in `reserved`, change the token type to the reserved name.
    r"[A-Za-z_][A-Za-z0-9_]*"
    if t.value in reserved:
        t.type = reserved[t.value]
    return t


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    # Report illegal character and skip it so lexer can continue.
    print(f"Line {t.lineno}: lexical error: illegal character {t.value[0]!r}")
    t.lexer.skip(1)


def _find_column(source, lexpos):
    last_nl = source.rfind("\n", 0, lexpos)
    return lexpos - last_nl


def tokenize_all(source):# 
    """runs the lexer to completion and stores every token
      in token_log for the output file.
      This is separate from the lexer used by the parser"""
    token_log.clear()
    lx = lex.lex(errorlog=lex.NullLogger())
    lx.input(source)
    idx = 0
    while True:
        tok = lx.token()
        if tok is None:
            break
        token_log.append({
            "idx":   idx,
            "type":  tok.type,
            "value": tok.value,
            "line":  tok.lineno,
            "col":   _find_column(source, tok.lexpos),
        })
        idx += 1
    return token_log


def build_lexer():
    # creates a fresh lexer instance specifically for the parse
    return lex.lex(errorlog=lex.NullLogger())


def render_tokens():
    out = []
    out.append(f"{'#':<4}{'Type':<12}{'Value':<22}{'Line':<6}{'Col'}")
    out.append("-" * 54)
    for t in token_log:
        v = repr(t["value"])
        if len(v) > 20:
            v = v[:17] + "..."
        out.append(f"{t['idx']:<4}{t['type']:<12}{v:<22}{t['line']:<6}{t['col']}")
    return "\n".join(out)
