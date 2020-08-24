from enum import Enum
import re


class Op(Enum):
    FUNC = 0x00

    CONST_NULL = 0x10
    CONST_FALSE = 0x11
    CONST_TRUE = 0x12
    CONST_INT = 0x13
    CONST_INT_BIG = 0x14
    CONST_STRING = 0x15

    OP_NEG = 0x20
    OP_ADD = 0x21
    OP_SUB = 0x22
    OP_MUL = 0x23
    OP_DIV = 0x24
    OP_MOD = 0x25

    OP_NOT = 0x28
    OP_AND = 0x29
    OP_OR = 0x2A

    CMP_EQ = 0x30
    CMP_NE = 0x31
    CMP_LT = 0x32
    CMP_LTE = 0x33
    CMP_GT = 0x34
    CMP_GTE = 0x35

    DUP = 0x40
    DROP = 0x41

    # LOAD_GLOBAL = 0x48
    # STORE_GLOBAL = 0x49
    LOAD_LOCAL = 0x4A
    STORE_LOCAL = 0x4B

    CHECK = 0x50
    JUMP = 0x51
    RET = 0x52
    CALL = 0x53
    CALL_NATIVE = 0x54


class Param(Enum):
    STRING = 0
    UINT = 1
    INT = 2
    INT_BIG = 3


PARAMS = {
    Op.FUNC: [Param.STRING, Param.UINT, Param.UINT],
    Op.CONST_INT: [Param.INT],
    Op.CONST_INT_BIG: [Param.INT_BIG],
    Op.CONST_STRING: [Param.STRING],
    Op.LOAD_LOCAL: [Param.UINT],
    Op.STORE_LOCAL: [Param.UINT],

    Op.JUMP: [Param.INT],
    Op.CALL: [Param.STRING, Param.UINT],
    Op.CALL_NATIVE: [Param.STRING, Param.UINT]
}


class ProgramError(Exception):
    def __init__(self, pos, message):
        self.pos = pos
        self.message = message

    def __str__(self):
        return f'{self.pos:04X}: {self.message}'


class Program:
    def __init__(self, data):
        self.buf = bytearray(data)
        self.pos = 0

    def read_instr(self):
        op_code = self.read_uint()
        try:
            op = Op(op_code)
        except ValueError:
            raise ProgramError(self.pos, f'{op_code:02X} is not a valid op code')

        params = PARAMS.get(op, [])
        args = []
        for param in params:
            if param == Param.STRING:
                args.append(self.read_string())
            elif param == Param.UINT:
                args.append(self.read_uint())
            elif param == Param.INT:
                args.append(self.read_int())
            elif param == Param.INT_BIG:
                args.append(self.read_int_big())
            else:
                assert False, param
        return op, args

    def read_uint(self):
        if self.pos >= len(self.buf):
            raise ProgramError(self.pos, 'unexpected end of input')

        result = self.buf[self.pos]
        self.pos += 1
        return result

    def read_int(self):
        result = self.read_uint()
        if result & 0x80:
            result -= 0x100
        return result

    def read_int_big(self):
        r1 = self.read_uint()
        r2 = self.read_uint()
        r3 = self.read_uint()
        r4 = self.read_uint()
        result = r1 + (r2 << 8) + (r3 << 16) + (r4 << 24)
        if result & 0x8000_0000:
            result -= 0x1_0000_0000
        return result

    def read_string(self):
        length = self.read_uint()
        if self.pos + length > len(self.buf):
            raise ProgramError(self.pos, 'unexpected end of input inside a string')
        data = self.buf[self.pos:self.pos + length]
        try:
            result = data.decode('ascii')
        except UnicodeDecodeError:
            raise ProgramError(self.pos, f'string is not ASCII: {data}')
        self.pos += length
        return result

    def iter(self):
        self.pos = 0
        while self.pos < len(self.buf):
            pos = self.pos
            op, args = self.read_instr()
            yield pos, op, args


class Disassembler:
    def __init__(self, program, hex=True, color=True):
        self.program = program
        self.hex = hex
        self.color = color

        self.targets = {}

    def comment(self, s):
        if self.color:
            return '\x1b[90m' + s + '\x1b[0m'
        return s

    def number(self, s):
        if self.color:
            return '\x1b[34m' + s + '\x1b[0m'
        return s

    def string(self, s):
        if self.color:
            return '\x1b[93m' + s + '\x1b[0m'
        return s

    def label(self, s):
        if self.color:
            return '\x1b[96m' + s + '\x1b[0m'
        return s

    def dump(self):
        self.collect_labels()

        lines = []
        for pos, op, args in self.program.iter():
            if op == Op.FUNC:
                lines.append('')

            if pos in self.targets:
                lines.append(self.label(self.targets[pos]) + ':')

            if op == Op.FUNC:
                line = self.dump_instr(op, args)
            elif op == Op.JUMP:
                target = pos + args[0]
                if target in self.targets:
                    label = self.targets[target]
                    line = f'    JUMP {self.label(label)}  '
                    line += self.comment(f'# {args[0]:+}, {target:04X}')
                else:
                    line = f'    JUMP {args[0]}  '
                    line += self.comment(f'# {args[0]:+}, {target:04X} (unknown)')
            else:
                line = '    ' + self.dump_instr(op, args)

            if self.hex:
                data = self.program.buf[pos:self.program.pos]
                hex = self.dump_hex(pos, data)
                line = self.ljust(line, 50) + hex

            lines.append(line)

        return '\n'.join(lines) + '\n'

    def ljust(self, line, width):
        if self.color:
            length = len(re.sub(r'\x1b.*?m', '', line))
        else:
            length = len(line)

        pad = width - length
        if pad > 0:
            line += ' ' * pad
        return line

    def dump_hex(self, pos, data):
        line = f'# {pos:04X}: '
        for byte in data:
            line += f' {byte:02X}'
        return self.comment(line)

    def collect_labels(self):
        self.targets.clear()

        positions = set()
        for pos, op, args in self.program.iter():
            if op != Op.FUNC:
                positions.add(pos)

        counter = 1

        for pos, op, args in self.program.iter():
            if op == Op.JUMP:
                target = pos + args[0]
                if target not in positions:
                    # invalid/unaligned target, do not translate
                    continue
                if target not in self.targets:
                    label = f'L{counter}'
                    self.targets[target] = label
                    counter += 1

    def dump_instr(self, op, args):
        result = op.name

        params = PARAMS.get(op, [])
        for param, arg in zip(params, args):
            result += ' '
            if param == Param.STRING:
                result += self.string(repr(arg))
            else:
                assert isinstance(arg, int)
                result += self.number(str(arg))

        return result


if __name__ == '__main__':
    code = b''
    code += b'\x00\x05hello\x00\x02'
    code += b'\x13\x02'
    code += b'\x13\x03'
    code += b'\x21'
    code += b'\x51\xFD'
    code += b'\x51\xFF'
    code += b'\x51\x02'
    code += b'\x54\x05print\x01'

    program = Program(code)
    print(Disassembler(program).dump())
