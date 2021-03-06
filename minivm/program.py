from enum import Enum
import unittest


HEADER = b'MINIVM\0\0'


class Op(Enum):
    FUNC = 0x01

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

    CMP_EQ = 0x30
    CMP_NE = 0x31
    CMP_LT = 0x32
    CMP_LTE = 0x33
    CMP_GT = 0x34
    CMP_GTE = 0x35

    DUP = 0x40
    DROP = 0x41

    LOAD_GLOBAL = 0x48
    STORE_GLOBAL = 0x49
    LOAD_LOCAL = 0x4A
    STORE_LOCAL = 0x4B

    JUMP = 0x50
    JUMP_IF = 0x51
    RET = 0x58
    CALL = 0x59
    CALL_VOID = 0x5A


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
    Op.LOAD_GLOBAL: [Param.STRING],
    Op.STORE_GLOBAL: [Param.STRING],
    Op.LOAD_LOCAL: [Param.UINT],
    Op.STORE_LOCAL: [Param.UINT],
    Op.JUMP: [Param.INT_BIG],
    Op.JUMP_IF: [Param.INT_BIG],
    Op.CALL: [Param.STRING, Param.UINT],
    Op.CALL_VOID: [Param.STRING, Param.UINT],
}


class ProgramError(Exception):
    def __init__(self, pos, message):
        self.pos = pos
        self.message = message

    def __str__(self):
        return f"{self.pos:04X}: {self.message}"


class Program:
    def __init__(self, bytecode):
        self.buf = bytes(bytecode)
        if not self.buf.startswith(HEADER):
            raise ProgramError(0, "Program doesn't start with a header")
        self.pos = len(HEADER)

    def read_instr(self):
        op_code = self.read_uint()
        try:
            op = Op(op_code)
        except ValueError:
            raise ProgramError(self.pos, f"{op_code:02X} is not a valid op code")

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

    def read_from(self, pos):
        self.pos = pos
        op, args = self.read_instr()
        length = self.pos - pos
        return length, op, args

    def read_uint(self):
        if self.pos >= len(self.buf):
            raise ProgramError(self.pos, "unexpected end of input")

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
        result = r1 + (r2 << 8)
        if result & 0x8000:
            result -= 0x10000
        return result

    def read_string(self):
        length = self.read_uint()
        if self.pos + length > len(self.buf):
            raise ProgramError(self.pos, "unexpected end of input inside a string")
        data = self.buf[self.pos : self.pos + length]
        try:
            result = data.decode("ascii")
        except UnicodeDecodeError:
            raise ProgramError(self.pos, f"string is not ASCII: {data}")
        self.pos += length
        return result

    def iter(self):
        self.pos = len(HEADER)
        while self.pos < len(self.buf):
            pos = self.pos
            op, args = self.read_instr()
            length = self.pos - pos
            yield pos, length, op, args


class ProgramTest(unittest.TestCase):
    def test_instructions(self):
        data = [
            *HEADER,
            Op.FUNC.value, 3, *b'foo', 4, 5,
            Op.CONST_INT.value, 0xFF,
            Op.CONST_INT_BIG.value, 0xFF, 0x01,
            Op.CALL.value, 3, *b'bar', 5,
        ]
        program = Program(data)
        self.assertListEqual(list(program.iter()), [
            (8, 7, Op.FUNC, ['foo', 4, 5]),
            (15, 2, Op.CONST_INT, [-1]),
            (17, 3, Op.CONST_INT_BIG, [0x1FF]),
            (20, 6, Op.CALL, ['bar', 5]),
        ])
