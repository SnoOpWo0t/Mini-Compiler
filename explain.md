Explain: folders and files
=========================

Short, simple explanation of why folders exist and what files do.

1) `input/` — source examples
- Holds example C files used to test compiler features.
- Each file isolates one feature: loops, functions, arrays, errors, etc.
- Why: keeps test programs separate from code and outputs so you can run and debug easily.

2) `output/` — phase outputs
- Stores artifacts produced by each compiler phase so you can inspect them:
  - `tokens.txt`: lexer token list (from `src/lexer.py`).
  - `ast.txt`: parsed AST pretty-print (from `src/parser.py` + `src/ast_nodes.py`).
  - `symbol_table.txt`: symbol table and semantic errors (from `src/semantic.py` + `src/symbol_table.py`).
  - `tac.txt`: three-address code IR (from `src/codegen.py`, `TacGenerator`).
  - `assembly.asm`: target-like assembly (from `src/codegen.py`, `tac_to_asm`).
- Why: inspect intermediate representations, find which phase causes bugs.

3) `src/` — compiler source (what each file does)
- `lexer.py`: Phase 1. Token rules and functions `build_lexer()` and `tokenize_all(source)`.
  How: regex rules produce tokens with type, value, line/col.
- `parser.py`: Phase 2. Grammar rules (`p_` functions). `build_parser()` builds parser.
  How: PLY yacc parses tokens -> calls actions -> builds AST nodes (from `ast_nodes.py`).
- `ast_nodes.py`: AST dataclasses and `ast_str()` pretty-printer used for `ast.txt`.
- `symbol_table.py`: `Symbol` and `SymbolTable` store scopes, lookup/insert, render table.
- `semantic.py`: Phase 3. `Semantic` visitor builds symbol table and checks types/scopes.
  How: walk AST, insert symbols, check redeclarations, type coercion, return/arg checks.
- `codegen.py`: Phase 4 + 5. `TacGenerator` makes TAC; `tac_to_asm` converts TAC to assembly.
- `main.py`: driver. Runs phases in order and writes `output/*` files.

Pipeline (one line):
`source.c` -> `lexer.py` -> `parser.py` -> `semantic.py` -> `codegen.py` -> `output/*`

Run example:
```
python src/main.py input/sample.c
```

If you want this shorter (caveman style) say so and I will rewrite very terse.
