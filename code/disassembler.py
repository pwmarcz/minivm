import re
import unittest

from .program import Op, PARAMS, Param, Program
from .tokens import escape_string


class Disassembler:
    def __init__(self, program, hex=True, color=True):
        self.program = program
        self.hex = hex
        self.color = color

        self.targets = {}

    def comment(self, s):
        if self.color:
            return "\x1b[90m" + s + "\x1b[0m"
        return s

    def number(self, s):
        if self.color:
            return "\x1b[34m" + s + "\x1b[0m"
        return s

    def string(self, s):
        if self.color:
            return "\x1b[93m" + s + "\x1b[0m"
        return s

    def label(self, s):
        if self.color:
            return "\x1b[96m" + s + "\x1b[0m"
        return s

    def dump(self):
        self.collect_labels()

        lines = []
        for pos, length, op, args in self.program.iter():
            if op == Op.FUNC:
                lines.append("")

            if pos in self.targets:
                lines.append(self.label(self.targets[pos]) + ":")

            if op == Op.FUNC:
                line = self.dump_instr(op, args)
            elif op == Op.JUMP:
                target = pos + args[0]
                if target in self.targets:
                    label = self.targets[target]
                    line = f"    JUMP {self.label(label)}  "
                    line += self.comment(f"# {args[0]:+}, {target:04X}")
                else:
                    line = f"    JUMP {args[0]}  "
                    line += self.comment(f"# {args[0]:+}, {target:04X} (unknown)")
            else:
                line = "    " + self.dump_instr(op, args)

            if self.hex:
                data = self.program.buf[pos : pos + length]
                hex = self.dump_hex(pos, data)
                line = self.ljust(line, 50) + hex

            lines.append(line)

        return "\n".join(lines) + "\n"

    def ljust(self, line, width):
        if self.color:
            length = len(re.sub(r"\x1b.*?m", "", line))
        else:
            length = len(line)

        pad = width - length
        if pad > 0:
            line += " " * pad
        return line

    def dump_hex(self, pos, data):
        line = f"# {pos:04X}: "
        for byte in data:
            line += f" {byte:02X}"
        return self.comment(line)

    def collect_labels(self):
        self.targets.clear()

        positions = set()
        for pos, length, op, args in self.program.iter():
            if op != Op.FUNC:
                positions.add(pos)

        counter = 1

        for pos, length, op, args in self.program.iter():
            if op == Op.JUMP:
                target = pos + args[0]
                if target not in positions:
                    # invalid/unaligned target, do not translate
                    continue
                if target not in self.targets:
                    label = f"L{counter}"
                    self.targets[target] = label
                    counter += 1

    def dump_instr(self, op, args):
        result = op.name

        params = PARAMS.get(op, [])
        for param, arg in zip(params, args):
            result += " "
            if param == Param.STRING:
                result += self.string(escape_string(arg))
            else:
                assert isinstance(arg, int)
                result += self.number(str(arg))

        return result


class DisassemblerTest(unittest.TestCase):
    def test(self):
        data = [
            Op.FUNC.value, 5, *b'hello', 0, 2,
            Op.CONST_INT.value, 2,
            Op.CONST_INT.value, 3,
            Op.OP_ADD.value,
            Op.JUMP.value, 6,
            Op.JUMP.value, 0x100-3,
            Op.JUMP.value, 0x100-1,
            Op.CALL_NATIVE.value, 5, *b'print', 1,
            Op.RET.value,
        ]
        program = Program(data)
        dis = Disassembler(program, hex=False, color=False).dump()
        self.assertEqual(dis, '''\

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
''')


def main():
    code = b""
    code += b"\x00\x05hello\x00\x02"
    code += b"\x13\x02"
    code += b"\x13\x03"
    code += b"\x21"
    code += b"\x51\xFD"
    code += b"\x51\xFF"
    code += b"\x51\x02"
    code += b"\x54\x05prin\x01\x01"

    program = Program(code)
    print(Disassembler(program).dump())


if __name__ == '__main__':
    main()
