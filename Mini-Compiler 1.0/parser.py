from dataclasses import dataclass

@dataclass
class Program:
    statements: list


@dataclass
class Block:
    statements: list


@dataclass
class FunctionDef:
    return_type: str
    name: str
    params: list
    body: Block


@dataclass
class Parameter:
    type: str
    name: str


@dataclass
class Declaration:
    type: str
    name: str
    initializer: object | None


@dataclass
class Assignment:
    name: str
    value: object


@dataclass
class PrintStatement:
    value: object


@dataclass
class IfStatement:
    condition: object
    then_branch: Block
    else_branch: Block | None


@dataclass
class WhileStatement:
    condition: object
    body: Block


@dataclass
class ReturnStatement:
    value: object | None


@dataclass
class ExpressionStatement:
    value: object


@dataclass
class BinaryOp:
    left: object
    operator: str
    right: object


@dataclass
class UnaryOp:
    operator: str
    operand: object


@dataclass
class Number:
    value: int


@dataclass
class Identifier:
    name: str


@dataclass
class Call:
    name: str
    args: list


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def current(self):
        return self.tokens[self.index]

    def peek(self, offset=1):
        index = self.index + offset
        if index < len(self.tokens):
            return self.tokens[index]
        return self.tokens[-1]

    def advance(self):
        token = self.current()
        self.index += 1
        return token

    def match(self, expected_type, expected_value=None):
        token = self.current()

        if token.type == expected_type and (expected_value is None or token.value == expected_value):
            self.index += 1
            return token

        expected = expected_type if expected_value is None else f'{expected_type}({expected_value})'
        raise SyntaxError(f'Expected {expected} at line {token.line}, column {token.column}')

    def check(self, token_type, value=None):
        token = self.current()
        return token.type == token_type and (value is None or token.value == value)

    def parse_program(self):
        statements = []

        while not self.check('EOF'):
            statements.append(self.parse_toplevel())

        return Program(statements)

    def parse_toplevel(self):
        if self.check('KEYWORD', 'int') or self.check('KEYWORD', 'void'):
            token_type = self.advance().value
            name = self.match('ID').value

            if self.check('LPAREN'):
                return self.parse_function(token_type, name)

            initializer = None
            if self.check('ASSIGN'):
                self.advance()
                initializer = self.parse_expression()

            self.match('SEMICOLON')
            return Declaration(token_type, name, initializer)

        return self.parse_statement()

    def parse_function(self, return_type, name):
        self.match('LPAREN')
        params = []

        if not self.check('RPAREN'):
            while True:
                param_type = self.match('KEYWORD').value
                param_name = self.match('ID').value
                params.append(Parameter(param_type, param_name))

                if not self.check('COMMA'):
                    break
                self.advance()

        self.match('RPAREN')
        body = self.parse_block()
        return FunctionDef(return_type, name, params, body)

    def parse_statement(self):
        if self.check('LBRACE'):
            return self.parse_block()

        if self.check('KEYWORD', 'int') or self.check('KEYWORD', 'void'):
            statement_type = self.advance().value
            name = self.match('ID').value
            initializer = None

            if self.check('ASSIGN'):
                self.advance()
                initializer = self.parse_expression()

            self.match('SEMICOLON')
            return Declaration(statement_type, name, initializer)

        if self.check('KEYWORD', 'print'):
            self.advance()
            self.match('LPAREN')
            value = self.parse_expression()
            self.match('RPAREN')
            self.match('SEMICOLON')
            return PrintStatement(value)

        if self.check('KEYWORD', 'if'):
            self.advance()
            self.match('LPAREN')
            condition = self.parse_expression()
            self.match('RPAREN')
            then_branch = self.parse_block()
            else_branch = None

            if self.check('KEYWORD', 'else'):
                self.advance()
                else_branch = self.parse_block()

            return IfStatement(condition, then_branch, else_branch)

        if self.check('KEYWORD', 'while'):
            self.advance()
            self.match('LPAREN')
            condition = self.parse_expression()
            self.match('RPAREN')
            body = self.parse_block()
            return WhileStatement(condition, body)

        if self.check('KEYWORD', 'return'):
            self.advance()
            value = None if self.check('SEMICOLON') else self.parse_expression()
            self.match('SEMICOLON')
            return ReturnStatement(value)

        if self.check('ID') and self.peek().type == 'ASSIGN':
            name = self.advance().value
            self.match('ASSIGN')
            value = self.parse_expression()
            self.match('SEMICOLON')
            return Assignment(name, value)

        expression = self.parse_expression()
        self.match('SEMICOLON')
        return ExpressionStatement(expression)

    def parse_block(self):
        self.match('LBRACE')
        statements = []

        while not self.check('RBRACE'):
            statements.append(self.parse_statement())

        self.match('RBRACE')
        return Block(statements)

    def parse_expression(self):
        return self.parse_equality()

    def parse_equality(self):
        expression = self.parse_comparison()

        while self.check('REL') and self.current().value in ('==', '!='):
            operator = self.advance().value
            right = self.parse_comparison()
            expression = BinaryOp(expression, operator, right)

        return expression

    def parse_comparison(self):
        expression = self.parse_term()

        while self.check('REL') and self.current().value in ('<', '>', '<=', '>='):
            operator = self.advance().value
            right = self.parse_term()
            expression = BinaryOp(expression, operator, right)

        return expression

    def parse_term(self):
        expression = self.parse_factor()

        while self.check('OP') and self.current().value in ('+', '-'):
            operator = self.advance().value
            right = self.parse_factor()
            expression = BinaryOp(expression, operator, right)

        return expression

    def parse_factor(self):
        expression = self.parse_unary()

        while self.check('OP') and self.current().value in ('*', '/'):
            operator = self.advance().value
            right = self.parse_unary()
            expression = BinaryOp(expression, operator, right)

        return expression

    def parse_unary(self):
        if self.check('OP') and self.current().value in ('-', '+'):
            operator = self.advance().value
            operand = self.parse_unary()
            return UnaryOp(operator, operand)

        return self.parse_primary()

    def parse_primary(self):
        token = self.current()

        if token.type == 'NUMBER':
            self.advance()
            return Number(int(token.value))

        if token.type == 'ID':
            name = self.advance().value

            if self.check('LPAREN'):
                self.advance()
                args = []

                if not self.check('RPAREN'):
                    while True:
                        args.append(self.parse_expression())
                        if not self.check('COMMA'):
                            break
                        self.advance()

                self.match('RPAREN')
                return Call(name, args)

            return Identifier(name)

        if token.type == 'LPAREN':
            self.advance()
            expression = self.parse_expression()
            self.match('RPAREN')
            return expression

        raise SyntaxError(f'Invalid expression at line {token.line}, column {token.column}')