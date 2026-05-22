class CodeGenerator:
    def __init__(self):
        self.asm = []

    def generate(self, tac_lines):
        self.asm = []

        for instruction in tac_lines:
            op = instruction.op

            if op == 'FUNC':
                self.asm.append(f'{instruction.arg1}:')
                self.asm.append(f'  ; params = {instruction.arg2}')
            elif op == 'END_FUNC':
                self.asm.append(f'  ; end {instruction.arg1}')
            elif op == 'PARAM':
                self.asm.append(f'  ; param {instruction.arg1}')
            elif op == 'LABEL':
                self.asm.append(f'{instruction.arg1}:')
            elif op == 'JMP':
                self.asm.append(f'  JMP {instruction.arg1}')
            elif op == 'JZ':
                self.asm.append(f'  CMP {instruction.arg1}, 0')
                self.asm.append(f'  JE {instruction.result}')
            elif op == 'PRINT':
                self.asm.append(f'  PRINT {instruction.arg1}')
            elif op == 'RETURN':
                if instruction.arg1 is not None:
                    self.asm.append(f'  MOV R1, {instruction.arg1}')
                self.asm.append('  RET')
            elif op == 'ARG':
                self.asm.append(f'  PUSH {instruction.arg1}')
            elif op == 'CALL':
                self.asm.append(f'  CALL {instruction.arg1}, {instruction.arg2}')
                self.asm.append(f'  MOV {instruction.result}, R1')
            elif op == '=':
                self.asm.append(f'  MOV {instruction.result}, {instruction.arg1}')
            elif op == 'NEG':
                self.asm.append('  MOV R1, 0')
                self.asm.append(f'  SUB R1, {instruction.arg1}')
                self.asm.append(f'  MOV {instruction.result}, R1')
            elif op in ('+', '-', '*', '/', '==', '!=', '<', '<=', '>', '>='):
                self.asm.append(f'  MOV R1, {instruction.arg1}')
                if op == '+':
                    self.asm.append(f'  ADD R1, {instruction.arg2}')
                elif op == '-':
                    self.asm.append(f'  SUB R1, {instruction.arg2}')
                elif op == '*':
                    self.asm.append(f'  MUL R1, {instruction.arg2}')
                elif op == '/':
                    self.asm.append(f'  DIV R1, {instruction.arg2}')
                else:
                    jump_map = {
                        '==': 'SETE',
                        '!=': 'SETNE',
                        '<': 'SETL',
                        '<=': 'SETLE',
                        '>': 'SETG',
                        '>=': 'SETGE',
                    }
                    self.asm.append(f'  CMP R1, {instruction.arg2}')
                    self.asm.append(f'  {jump_map[op]} R1')

                self.asm.append(f'  MOV {instruction.result}, R1')

        return self.asm
