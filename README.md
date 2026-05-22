# Mini C Compiler (Python)

Pipeline: **source → tokens → AST → symbol table → TAC → assembly**.

## Project Layout

```
mini_compiler_py/
├── Makefile
├── README.md
├── requirements.txt
├── .gitignore
├── slide.md / slide_18.md     # presentation decks
├── src/                       # compiler source
│   ├── lexer.py               # Phase 1 — PLY lex
│   ├── parser.py              # Phase 2 — PLY yacc
│   ├── ast_nodes.py           # AST dataclasses + pretty-printer
│   ├── symbol_table.py        # scoped symbol table
│   ├── semantic.py            # Phase 3 — type / scope checks
│   ├── codegen.py             # Phase 4 (TAC) + Phase 5 (asm)
│   └── main.py                # driver — runs all 5 phases
├── input/                     # test source programs (one feature each)
│   ├── sample.c               # basic types + if/else + while
│   ├── for_loop.c             # for-loop demo
│   ├── functions.c            # function + recursion
│   ├── arrays.c               # array decl + read + write
│   └── errors.c               # semantic error demo
└── output/                    # generated per-phase artefacts
    ├── tokens.txt
    ├── ast.txt
    ├── symbol_table.txt
    ├── tac.txt
    └── assembly.asm
```

## Setup

```powershell
pip install -r requirements.txt
```

## Run

```powershell
python src/main.py input/sample.c
python src/main.py input/functions.c
python src/main.py input/arrays.c
python src/main.py input/for_loop.c
python src/main.py input/errors.c
python src/main.py input/strings.c
```

After a run, look in `output/` for per-phase dumps.

## Supported Language Features

| Category   | Features                                                          |
|------------|-------------------------------------------------------------------|
| Types      | `int`, `float`, `void`, `char`                                    |
| Literals   | int, float, string                                                |
| Arithmetic | `+ - * / %` and unary `-`                                         |
| Relational | `< > <= >= == !=`                                                 |
| Logical    | `&& || !`                                                         |
| Control    | `if / else`, `while`, `for`                                       |
| Functions  | multi-param, recursion, `void`, `return`                          |
| I/O        | `printf(arg1, arg2, ...)` — multi-argument                        |
| Comments   | `// line` and `/* block */`                                       |
| Scoping    | global + per-function scopes, parameter shadowing                 |

## Phases

| Phase | Module                                  | Output                                  |
|-------|-----------------------------------------|-----------------------------------------|
| 1     | `lexer.py` (PLY lex)                    | `output/tokens.txt`                     |
| 2     | `parser.py` (PLY yacc → AST)            | `output/ast.txt`                        |
| 3     | `semantic.py` + `symbol_table.py`       | `output/symbol_table.txt`               |
| 4     | `codegen.py` (`TacGenerator`)           | `output/tac.txt`                        |
| 5     | `codegen.py` (`tac_to_asm`)             | `output/assembly.asm`                   |

## Error Detection

| Layer    | Examples                                                            |
|----------|---------------------------------------------------------------------|
| Lexical  | illegal character                                                   |
| Syntax   | missing `;`, malformed expression                                   |
| Semantic | redeclaration, undeclared id, type mismatch, return / arg mismatch  |

After any error → compilation halts. Earlier phase artefacts are preserved.

## Tooling

Built on **PLY** (Python Lex-Yacc, by David Beazley) — same Lex/YACC formalism
(DFA-based regex tokenizer + LALR(1) parser) as `flex` / `bison`, running in
Python without an external compile step.

