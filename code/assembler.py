import unittest
import argparse
from pathlib import Path
import sys

from .program import Param, PARAMS, Op
from .tokens import ParseError, Scanner, TIdent, TLabel, TString, TInteger


class Assembler:
    def __init__(self, code):
        self.lines = code.splitlines()
        self.data = bytearray()
        self.targets = {}
        self.sources = {}
        self.errors = []

    def parse_param(self, token, param):
        if param == Param.STRING:
            if not isinstance(token, TString):
                raise ParseError(token.lineno, token.col, f"expected string, got {token:r}")
            if len(token.value) > 256:
                raise ParseError(token.lineno, token.col, "string literal too long")

            token_bytes = token.value.encode('ascii')
            return bytes([len(token_bytes)]) + token_bytes

        if not isinstance(token, TInteger):
            raise ParseError(token.lineno, token.col, f"expected number, got {token}")

        min_val, max_val = {
            Param.UINT: (0, 0xFF),
            Param.INT: (-0x80, 0x7F),
            Param.INT_BIG: (-0x8000_0000, 0x7FFF_FFFF),
        }[param]

        value = token.value

        if not min_val <= value <= max_val:
            raise ParseError(
                token.lineno, token.col,
                f"number should be between {min_val} and {max_val}: {value}"
            )

        if param == Param.UINT:
            return bytes([value])
        elif param == Param.INT:
            if value < 0:
                value += 0x100
            return bytes([value])
        elif param == Param.INT_BIG:
            if value < 0:
                value += 0x1_0000_0000
            return bytes(
                [
                    value & 0xFF,
                    (value >> 8) & 0xFF,
                    (value >> 16) & 0xFF,
                    (value >> 24) & 0xFF,
                ]
            )

    def parse_line(self, tokens, program_pos):
        if not tokens:
            return b''

        if isinstance(tokens[0], TLabel):
            label = tokens[0].value.upper()
            if label in self.targets:
                raise ParseError(tokens[0].lineno, tokens[0].col, f'duplicate label: {label}')
            self.targets[label] = program_pos
            tokens.pop(0)

        if not tokens:
            return b''

        op = self.parse_op_name(tokens[0])
        return self.parse_op(op, tokens, program_pos)

    def parse_op_name(self, token):
        if not isinstance(token, TIdent):
            raise ParseError(token.lineno, token.col, "operation name expected")
        op_name = token.value.upper()
        try:
            return Op[op_name]
        except KeyError:
            raise ParseError(token.lineno, token.col, f"unknown operation: {op_name}")

    def parse_op(self, op, tokens, program_pos):
        params = PARAMS.get(op, [])
        if len(tokens) - 1 != len(params):
            raise ParseError(tokens[0].lineno, tokens[0].col, f"wrong number of parameters for {op.name}")

        if op == Op.JUMP and isinstance(tokens[1], TIdent):
            label = tokens[1].value.upper()
            self.sources[program_pos + 1] = tokens[1], label
            return bytes([op.value, 0])

        result = bytearray()
        result.append(op.value)
        for token, param in zip(tokens[1:], params):
            result.extend(self.parse_param(token, param))
        return result

    def update_locations(self):
        for source, (token, label) in self.sources.items():
            if label not in self.targets:
                self.errors.append(
                    ParseError(token.lineno, token.col, f'unknown label: {label}'))
                continue

            target = self.targets[label]
            delta = target - source + 1
            if not -128 <= delta <= 127:
                self.errors.append(
                    ParseError(token.lineno, token.col, f'jump is too far: {delta}'))
            if delta < 0:
                self.data[source] = delta + 0x100
            else:
                self.data[source] = delta

    def assemble(self):
        for lineno, line in enumerate(self.lines):
            # tokenize
            scanner = Scanner(line, lineno)

            try:
                tokens = list(scanner.iter())
                compiled = self.parse_line(tokens, len(self.data))
            except ParseError as e:
                self.errors.append(e)
            else:
                self.data.extend(compiled)

        self.update_locations()

        if self.errors:
            return None

        return self.data

    def describe_errors(self):
        prefix = ' ' * 2
        for error in self.errors:
            yield f'{error.lineno}:{error.col}: error: {error.message}'
            yield prefix + self.lines[error.lineno]
            yield prefix + ' ' * error.col + '^'


class AssemblerTest(unittest.TestCase):
    def test_assemble(self):
        code = '''\

FUNC "hello" 0 2
    CONST_INT 2
    CONST_INT 3
L2:
    OP_ADD
    JUMP L1  # +6, 0014
    JUMP L2  # -3, 000D
    JUMP -1  # -1, 0011 (unknown)
L1:
    CALL_NATIVE "print" 1
    RET
'''
        asm = Assembler(code)
        data = asm.assemble()
        self.assertListEqual(list(data), [
            Op.FUNC.value, 5, *b'hello', 0, 2,
            Op.CONST_INT.value, 2,
            Op.CONST_INT.value, 3,
            Op.OP_ADD.value,
            Op.JUMP.value, 6,
            Op.JUMP.value, 0x100-3,
            Op.JUMP.value, 0x100-1,
            Op.CALL_NATIVE.value, 5, *b'print', 1,
            Op.RET.value,
        ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input_file', metavar='INPUT_FILE',
        help='input file, or - for stdin',
    )
    parser.add_argument(
        'output_file', metavar='OUTPUT_FILE',
        help='output file, or - for stdout',
    )

    args = parser.parse_args()

    if args.input_file == '-':
        code = sys.stdin.read()
    else:
        code = Path(args.input_file).read_text()

    asm = Assembler(code)
    bytecode = asm.assemble()

    if bytecode is None:
        for error_line in asm.describe_errors():
            print(error_line, file=sys.stderr)
        sys.exit(1)

    if args.output_file == '-':
        sys.stdout.buffer.write(bytecode)
    else:
        Path(args.output_file).write_bytes(bytecode)


if __name__ == '__main__':
    main()
