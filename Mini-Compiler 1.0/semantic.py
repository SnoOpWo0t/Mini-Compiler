from parser import (
    Assignment,
    BinaryOp,
    Block,
    Call,
    Declaration,
    ExpressionStatement,
    FunctionDef,
    Identifier,
    IfStatement,
    Number,
    PrintStatement,
    Program,
    ReturnStatement,
    UnaryOp,
    WhileStatement,
)


class SemanticError(Exception):
    pass


class SemanticAnalyzer:
    def __init__(self):
        self.scopes = [{}]
        self.functions = {}

    @property
    def symbol_table(self):
        return self.scopes[0]

    def current_scope(self):
        return self.scopes[-1]

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()

    def declare_variable(self, name, value=None):
        scope = self.current_scope()

        if name in scope:
            raise SemanticError(f'Variable {name} already declared in this scope')

        scope[name] = value

    def resolve_variable(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]

        raise SemanticError(f'Variable {name} not declared')

    def assign_variable(self, name, value):
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] = value
                return

        raise SemanticError(f'Variable {name} not declared')

    def declare_function(self, name, function_node):
        if name in self.functions:
            raise SemanticError(f'Function {name} already declared')
        self.functions[name] = function_node

    def analyze(self, program):
        if not isinstance(program, Program):
            raise SemanticError('Expected a program node')

        for statement in program.statements:
            if isinstance(statement, FunctionDef):
                self.declare_function(statement.name, statement)

        for statement in program.statements:
            self.visit(statement)

    def visit(self, node):
        if isinstance(node, Program):
            for statement in node.statements:
                self.visit(statement)
            return

        if isinstance(node, Block):
            self.push_scope()
            try:
                for statement in node.statements:
                    self.visit(statement)
            finally:
                self.pop_scope()
            return

        if isinstance(node, FunctionDef):
            self.push_scope()
            try:
                for parameter in node.params:
                    self.declare_variable(parameter.name)
                for statement in node.body.statements:
                    self.visit(statement)
            finally:
                self.pop_scope()
            return

        if isinstance(node, Declaration):
            self.declare_variable(node.name)
            if node.initializer is not None:
                self.visit(node.initializer)
                self.assign_variable(node.name, None)
            return

        if isinstance(node, Assignment):
            self.resolve_variable(node.name)
            self.visit(node.value)
            self.assign_variable(node.name, None)
            return

        if isinstance(node, PrintStatement):
            self.visit(node.value)
            return

        if isinstance(node, IfStatement):
            self.visit(node.condition)
            self.visit(node.then_branch)
            if node.else_branch is not None:
                self.visit(node.else_branch)
            return

        if isinstance(node, WhileStatement):
            self.visit(node.condition)
            self.visit(node.body)
            return

        if isinstance(node, ReturnStatement):
            if node.value is not None:
                self.visit(node.value)
            return

        if isinstance(node, ExpressionStatement):
            self.visit(node.value)
            return

        if isinstance(node, BinaryOp):
            self.visit(node.left)
            self.visit(node.right)
            return

        if isinstance(node, UnaryOp):
            self.visit(node.operand)
            return

        if isinstance(node, Identifier):
            self.resolve_variable(node.name)
            return

        if isinstance(node, Call):
            if node.name not in self.functions:
                raise SemanticError(f'Function {node.name} not declared')

            expected = len(self.functions[node.name].params)
            if len(node.args) != expected:
                raise SemanticError(f'Function {node.name} expects {expected} arguments but got {len(node.args)}')

            for arg in node.args:
                self.visit(arg)
            return

        if isinstance(node, Number):
            return

        raise SemanticError(f'Unsupported node: {type(node).__name__}')