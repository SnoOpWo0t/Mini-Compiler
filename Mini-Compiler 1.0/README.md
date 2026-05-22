# Mini Compiler

This project is a small compiler written in Python. It takes a simple C-like program and runs it through the main compiler phases:

1. Lexical analysis
2. Parsing
3. Semantic analysis
4. Intermediate code generation
5. Pseudo-assembly generation

The goal of the project is to show how a compiler works from source code to lower-level output in one connected flow.

## Purpose

This compiler is made for learning and demo use. It shows:

- how source code is broken into tokens
- how grammar rules build a parse tree
- how variables and functions are checked
- how three-address code is produced
- how that intermediate form can be turned into assembly-like instructions

It is not a full production compiler. It is a mini compiler for a small language.

## What Input It Expects

The compiler expects a text file or inline source code written in a small C-like language.

Supported language features include:

- variable declarations like `int a = 5;`
- assignments like `a = a + 1;`
- arithmetic expressions like `a + b * 2`
- comparison expressions like `a > 10`
- `if` / `else`
- `while`
- functions like `int add(int x, int y) { return x + y; }`
- function calls like `add(a, b)`
- `print(...)`
- `return`

Example input:

```c
int add(int x, int y) {
    return x + y;
}

int a = 5;
int b = 10;
int c;
c = add(a, b);

if (c > 10) {
    print(c);
} else {
    print(0);
}

while (a < b) {
    a = a + 1;
}
```

## How To Run It

Run the compiler with the built-in sample program:

```bash
python main.py
```

Or pass your own source file:

```bash
python main.py your_program.txt
```

## What Output It Shows

When you run it, the program prints each compiler phase in order.

### 1. Source Code

It first prints the source code being compiled.

### 2. Tokens

It prints the token stream from the lexer.

Example:

```text
Token(type='KEYWORD', value='int', line=2, column=1)
Token(type='ID', value='add', line=2, column=5)
Token(type='LPAREN', value='(', line=2, column=8)
```

### 3. Parser Result

It checks whether the syntax is valid and prints:

```text
Syntax Valid
```

### 4. Semantic Analysis

It prints the global symbol table and the declared functions.

Example:

```text
Global symbols: {'a': None, 'b': None, 'c': None}
Functions: ['add']
```

### 5. Three-Address Code

It prints the intermediate instructions generated from the program.

Example:

```text
Instruction(op='FUNC', arg1='add', arg2=2, result=None)
Instruction(op='+', arg1='x', arg2='y', result='t1')
Instruction(op='RETURN', arg1='t1', arg2=None, result=None)
```

### 6. Assembly Code

It prints the pseudo-assembly form.

Example:

```text
add:
  ; params = 2
  MOV R1, x
  ADD R1, y
  MOV t1, R1
  RET
```

## How The Project Works

The flow is:

1. `lexer.py` reads the text and turns it into tokens.
2. `parser.py` reads tokens and builds the program structure.
3. `semantic.py` checks scopes, declarations, and function calls.
4. `icg.py` converts the program into three-address code.
5. `codegen.py` converts the intermediate code into pseudo-assembly.
6. `main.py` connects all phases and prints the output.

## Notes

- If the input has a syntax problem, the parser raises an error.
- If a variable or function is used before declaration, the semantic phase raises an error.
- The generated assembly is educational pseudo-assembly, not real machine code.
