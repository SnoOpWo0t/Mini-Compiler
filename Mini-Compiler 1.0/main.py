import sys

from codegen import CodeGenerator
from icg import IntermediateCodeGenerator
from lexer import lexer
from parser import Parser
from semantic import SemanticAnalyzer


DEFAULT_SOURCE_CODE = '''
int add(int x, int y) {
    return x + y
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
'''


def print_section(title):
    print(f'\n===== {title} =====')


def compile_source(source_code):
    print_section('SOURCE CODE')
    print(source_code)

    print_section('TOKENS')
    tokens = lexer(source_code)
    for token in tokens:
        print(token)

    print_section('PARSER')
    parser = Parser(tokens)
    program = parser.parse_program()
    print('Syntax Valid')

    print_section('SEMANTIC ANALYSIS')
    semantic = SemanticAnalyzer()
    semantic.analyze(program)
    print('Global symbols:', semantic.symbol_table)
    print('Functions:', list(semantic.functions.keys()))

    print_section('THREE ADDRESS CODE')
    icg = IntermediateCodeGenerator()
    tac = icg.generate(program)
    for instruction in tac:
        print(instruction)

    print_section('ASSEMBLY CODE')
    cg = CodeGenerator()
    assembly = cg.generate(tac)
    for line in assembly:
        print(line)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as source_file:
            source = source_file.read()
    else:
        source = DEFAULT_SOURCE_CODE

    compile_source(source)