from dataclasses import dataclass

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


@dataclass
class Instruction:
    op: str
    arg1: object = None
    arg2: object = None
    result: object = None


class IntermediateCodeGenerator:
    def __init__(self):
        self.temp_count = 1
        self.label_count = 1
        self.code = []

    def new_temp(self):
        temp = f't{self.temp_count}'
        self.temp_count += 1
        return temp

    def new_label(self, prefix='L'):
        label = f'{prefix}{self.label_count}'
        self.label_count += 1
        return label

    def emit(self, op, arg1=None, arg2=None, result=None):
        self.code.append(Instruction(op, arg1, arg2, result))

    def generate(self, node):
        self.code = []
        self.generate_node(node)
        return self.code

    def generate_node(self, node):
        if isinstance(node, Program):
            for statement in node.statements:
                self.generate_node(statement)
            return None

        if isinstance(node, Block):
            for statement in node.statements:
                self.generate_node(statement)
            return None

        if isinstance(node, FunctionDef):
            self.emit('FUNC', node.name, len(node.params))
            for parameter in node.params:
                self.emit('PARAM', parameter.name)
            self.generate_node(node.body)
            self.emit('END_FUNC', node.name)
            return None

        if isinstance(node, Declaration):
            if node.initializer is not None:
                value = self.generate_expression(node.initializer)
                self.emit('=', value, None, node.name)
            return None

        if isinstance(node, Assignment):
            value = self.generate_expression(node.value)
            self.emit('=', value, None, node.name)
            return None

        if isinstance(node, PrintStatement):
            value = self.generate_expression(node.value)
            self.emit('PRINT', value)
            return None

        if isinstance(node, IfStatement):
            false_label = self.new_label('ELSE')
            end_label = self.new_label('ENDIF')
            condition = self.generate_expression(node.condition)
            self.emit('JZ', condition, None, false_label)
            self.generate_node(node.then_branch)
            if node.else_branch is not None:
                self.emit('JMP', end_label)
                self.emit('LABEL', false_label)
                self.generate_node(node.else_branch)
                self.emit('LABEL', end_label)
            else:
                self.emit('LABEL', false_label)
            return None

        if isinstance(node, WhileStatement):
            start_label = self.new_label('WHILE')
            end_label = self.new_label('ENDWHILE')
            self.emit('LABEL', start_label)
            condition = self.generate_expression(node.condition)
            self.emit('JZ', condition, None, end_label)
            self.generate_node(node.body)
            self.emit('JMP', start_label)
            self.emit('LABEL', end_label)
            return None

        if isinstance(node, ReturnStatement):
            value = self.generate_expression(node.value) if node.value is not None else None
            self.emit('RETURN', value)
            return None

        if isinstance(node, ExpressionStatement):
            self.generate_expression(node.value)
            return None

        self.generate_expression(node)
        return None

    def generate_expression(self, node):
        if isinstance(node, Number):
            return str(node.value)

        if isinstance(node, Identifier):
            return node.name

        if isinstance(node, UnaryOp):
            operand = self.generate_expression(node.operand)
            if node.operator == '-':
                result = self.new_temp()
                self.emit('NEG', operand, None, result)
                return result
            return operand

        if isinstance(node, BinaryOp):
            left = self.generate_expression(node.left)
            right = self.generate_expression(node.right)
            result = self.new_temp()
            self.emit(node.operator, left, right, result)
            return result

        if isinstance(node, Call):
            for arg in node.args:
                self.emit('ARG', self.generate_expression(arg))
            result = self.new_temp()
            self.emit('CALL', node.name, len(node.args), result)
            return result

        return None

    def display(self):
        for instruction in self.code:
            print(instruction)