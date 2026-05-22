"""
Mini C compiler driver.
Usage:
    python src/main.py input/test_all.c
    PLY(python lex/yacc) is used for lexing and parsing. The compiler is organized into 5 phases:
1. Lexical analysis (tokenization)
2. Syntax analysis (parsing into AST)       
3. Semantic analysis (type checking, symbol table)
4. Intermediate code generation (TAC)
5. Target code generation (assembly)
Runs every compiler phase and writes:
    output/tokens.txt
    output/ast.txt
    output/symbol_table.txt
    output/tac.txt
    output/assembly.asm

A banner per phase is printed to stdout; full content goes to the files.
"""
import os
import sys
# Make sibling modules importable when run as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer       import tokenize_all, build_lexer, render_tokens   # noqa: E402
from parser      import build_parser, syntax_errors                # noqa: E402
from ast_nodes   import ast_str                                    # noqa: E402
from semantic    import Semantic                                   # noqa: E402
from codegen     import TacGenerator, tac_to_asm                   # noqa: E402

# Connections (how files interact):
# - `lexer.py` provides `tokenize_all`, `build_lexer`, `render_tokens` and
#   the `tokens` list used by `parser.py`. `main.py` calls `tokenize_all`


HERE    = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
OUT     = os.path.join(PROJECT, "output")
os.makedirs(OUT, exist_ok=True)
# `OUT` is the directory where every compiler phase writes its artifacts.
# This script orchestrates all phases in sequence and emits human-readable
# summaries to the console as well as full outputs to files.


def banner(title):
    line = "=" * 60
    print(f"\n{line}\n  {title}\n{line}")


def write(filename, text):
    path = os.path.join(OUT, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    print(text)
    print(f"\n[written to output/{filename}]")


def main():
    if len(sys.argv) < 2:
        print("Usage: python src/main.py <source.c>")
        sys.exit(2)

    path = sys.argv[1]
    if not os.path.isfile(path):
        print(f"Error: input file not found: {path}")
        sys.exit(2)

    with open(path, "r", encoding="utf-8") as f:
        source = f.read() # read your .c file

    print(f"Compiling: {path}")

    # ---- Phase 1: Lexical analysis ------------------------------------------
    banner("Phase 1: Lexical Analysis")
    tokenize_all(source)# Phase 1: tokenizes source and fills `token_log` in `lexer.py`
    write("tokens.txt", render_tokens())

    # ---- Phase 2: Parsing / AST --------------------------------------------
    banner("Phase 2: Syntax Analysis (AST)")
    lexer  = build_lexer() #build lexer instance
    parser = build_parser()# ply need parcer instance 
    ast    = parser.parse(source, lexer=lexer) # Phase 2: parses source into AST nodes; syntax errors go to `syntax_errors`

    if syntax_errors:
        for e in syntax_errors:
            print(f"  syntax error: {e}")
        write("ast.txt", "Parsing failed.\n" + "\n".join(syntax_errors))
        print("Parsing Failed")
        sys.exit(1)
    write("ast.txt", ast_str(ast))
    print("Parsing Successful")

    # ---- Phase 3: Semantic / Symbol table ----------------------------------
    banner("Phase 3: Semantic Analysis + Symbol Table")
    sem = Semantic()
    sem_errors = sem.analyze(ast)   # Phase 3: walks the AST, fills `sem.st` and collects semantic errors in `sem_errors`
    sym_text = sem.st.render()
    if sem_errors:
        sym_text += "\n\nSemantic Errors:\n"
        for e in sem_errors:
            sym_text += f"  - {e}\n"
    write("symbol_table.txt", sym_text)

    if sem_errors:
        for e in sem_errors:
            print(f"  semantic error: {e}")
        print("Compilation halted after Phase 3.")
        sys.exit(1)
    print("No semantic errors.")

    # ---- Phase 4: Three-address code ---------------------------------------
    banner("Phase 4: Intermediate Code (TAC)")
    gen = TacGenerator()
    tac = gen.gen(ast) # Phase 4: visits the AST to produce TAC; 

    # ---- Phase 5: Assembly --------------------------------------------------
    banner("Phase 5: Target Code Generation (Assembly)")
    asm = tac_to_asm(tac) # Phase 5
    write("assembly.asm", "\n".join(asm))

    banner("Compilation Successful")
    print(f"All phase outputs written to: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
