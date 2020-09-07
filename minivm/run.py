import argparse
from pathlib import Path
import sys
from collections import namedtuple

from .program import Program, Op, HEADER
from .assemble import run_assembler
from .disassemble import Disassembler

Function = namedtuple('Function', ['name', 'entry', 'n_params', 'n_locals'])


class MachineError(Exception):
    pass


class Frame:
    def __init__(self, name, ip, args, n_locals):
        self.name = name
        self.prev_ip = ip
        self.ip = ip
        self.stack = []
        self.locals = list(args)
        self.locals += [None] * n_locals


NATIVE_FUNCTIONS = {
    'print': (1, print),
}


STACK_LIMIT = 256


class Machine:
    def __init__(self, program: Program):
        self.program = program
        self.functions = {}
        for pos, length, op, args in program.iter():
            if op == Op.FUNC:
                name, n_params, n_locals = args
                entry = pos + length
                self.functions[name] = Function(name, entry, n_params, n_locals)
        self.frames = []
        self.globals = {}
        self.result = None
        self.skip = False

    def run(self):
        self.start()
        while self.running():
            self.step()
        return self.result

    def running(self):
        return len(self.frames) > 0

    def start(self):
        self.enter_function('main', [])

    def enter_function(self, name, args):
        if name not in self.functions:
            raise MachineError(f'Function not found: {name}')

        func = self.functions[name]
        if len(args) != func.n_params:
            raise MachineError(f'Function {name} expects {func.n_params} arguments, not {len(args)}')

        frame = Frame(name, func.entry, args, func.n_locals)
        self.frames.append(frame)

    def step(self):
        frame = self.frames[-1]
        length, op, args = self.program.read_from(frame.ip)
        frame.prev_ip = frame.ip
        frame.ip += length

        if self.skip:
            self.skip = False
            return

        if op == Op.FUNC:
            raise MachineError('trying to execute FUNC')
        elif op == Op.CONST_NULL:
            self.push(None)
        elif op == Op.CONST_FALSE:
            self.push(False)
        elif op == Op.CONST_TRUE:
            self.push(True)
        elif op in [Op.CONST_INT, Op.CONST_INT_BIG, Op.CONST_STRING]:
            self.push(args[0])

        elif op == Op.OP_NEG:
            val = self.pop()
            if not isinstance(val, int):
                raise MachineError(f'expecting an integer, not {val!r}')
            self.push(-val)

        elif op in [
            Op.OP_ADD,
            Op.OP_SUB,
            Op.OP_MUL,
            Op.OP_DIV,
            Op.OP_MOD,
        ]:
            self.handle_arith(op)

        elif op in [
            op.CMP_EQ,
            op.CMP_NE,
            op.CMP_LT,
            op.CMP_LTE,
            op.CMP_GT,
            op.CMP_GTE,
        ]:
            self.handle_cmp(op)

        elif op == Op.OP_NOT:
            val = self.pop()
            self.push(not val)

        elif op == op.DUP:
            val = self.pop()
            self.push(val)
            self.push(val)

        elif op == op.DROP:
            self.pop()

        elif op == op.LOAD_GLOBAL:
            name = args[0]
            if name not in self.globals:
                raise MachineError(f'Undefined global name: {name}')
            self.push(self.globals[name])

        elif op == op.STORE_GLOBAL:
            name = args[0]
            self.globals[name] = self.pop()

        elif op == op.LOAD_LOCAL:
            n = args[0]
            if not 0 <= n < len(frame.locals):
                raise MachineError(f'Invalid local number: {n}')
            self.push(frame.locals[n])

        elif op == op.STORE_LOCAL:
            n = args[0]
            if not 0 <= n < len(frame.locals):
                raise MachineError(f'Invalid local number: {n}')
            frame.locals[n] = self.pop()

        elif op == op.CHECK:
            val = self.pop()
            if not val:
                self.skip = True

        elif op == op.JUMP:
            frame.ip = frame.prev_ip + args[0]

        elif op == op.CALL:
            name, n_args = args
            self.handle_call(name, n_args)

        elif op == op.RET:
            val = None
            if frame.stack:
                val = self.pop()
            self.frames.pop()
            if self.frames:
                self.push(val)
            else:
                self.result = val
        else:
            assert False, op

    def handle_arith(self, op):
        a, b = self.pop_many(2)
        if not isinstance(a, int):
            raise MachineError(f'expecting an integer, not {a!r}')
        if not isinstance(b, int):
            raise MachineError(f'expecting an integer, not {b!r}')

        if op == Op.OP_ADD:
            result = a + b
        elif op == Op.OP_SUB:
            result = a - b
        elif op == Op.OP_MUL:
            result = a * b
        elif op == Op.OP_DIV:
            if b == 0:
                raise MachineError('division by 0')
            result = a // b
        elif op == Op.OP_MOD:
            if b == 0:
                raise MachineError('modulo by 0')
            result = a + b
        else:
            assert False, op

        self.push(result)

    def handle_cmp(self, op):
        a, b = self.pop_many(2)

        if op not in [Op.CMP_EQ, Op.CMP_NE]:
            if type(a) != type(b):
                raise MachineError(f'incompatible types for comparison: {a!r} and {b!r}')

        if op == Op.CMP_EQ:
            result = a == b
        elif op == Op.CMP_NE:
            result = a != b
        elif op == Op.CMP_LT:
            result = a < b
        elif op == Op.CMP_LTE:
            result = a <= b
        elif op == Op.CMP_GT:
            result = a > b
        elif op == Op.CMP_GTE:
            result = a >= b
        else:
            assert False, op

        self.push(result)

    def handle_call(self, name, n_args):
        args = self.pop_many(n_args)

        if name in self.functions:
            self.enter_function(name, args)
        elif name in NATIVE_FUNCTIONS:
            n_params, native_func = NATIVE_FUNCTIONS[name]
            if n_args != n_params:
                raise MachineError(
                    f'Function {name} expects {native_func.n_params} arguments, not {len(args)}'
                )

            try:
                result = native_func(*args)
            except Exception as e:
                raise MachineError(f'Error running native function {name}: {e}')
            self.push(result)
        else:
            raise MachineError(f'unknown function: {name}')

    def push(self, val):
        frame = self.frames[-1]
        if len(frame.stack) >= STACK_LIMIT:
            raise MachineError('stack overflow')
        frame.stack.append(val)

    def pop(self):
        frame = self.frames[-1]
        if len(frame.stack) < 1:
            raise MachineError('stack underflow')
        return frame.stack.pop()

    def pop_many(self, n):
        frame = self.frames[-1]
        if len(frame.stack) < n:
            raise MachineError('stack underflow')

        result = []
        for i in range(n):
            result.append(frame.stack.pop())
        result.reverse()
        return result

    def traceback(self):
        dis = Disassembler(self.program, color=True, hex=True)
        for frame in self.frames:
            # TODO colors
            yield f'{frame.prev_ip:04X}: ({frame.name})'
            length, op, args = self.program.read_from(frame.prev_ip)
            dump = dis.dump_line(frame.prev_ip, length, op, args)
            yield '  ' + dump


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input_file', metavar='INPUT_FILE',
        help='input file, or - for stdin',
    )

    args = parser.parse_args()

    if args.input_file == '-':
        data = sys.stdin.buffer.read()
    else:
        data = Path(args.input_file).read_bytes()

    if data.startswith(HEADER):
        bytecode = data
    else:
        bytecode = run_assembler(data.decode('ascii'))

    program = Program(bytecode)
    machine = Machine(program)

    try:
        result = machine.run()
        print(f'result: {result!r}')
    except MachineError as e:
        print('Traceback (most recent frame last):', file=sys.stderr)
        for error_line in machine.traceback():
            print(error_line, file=sys.stderr)
        print(f'error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
