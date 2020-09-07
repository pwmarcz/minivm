import argparse
import sys
from pathlib import Path
import curses

from .program import HEADER, Program
from .run import Machine
from .assemble import run_assembler
from .disassemble import Disassembler


class Debugger:
    def __init__(self, window, program):
        self.window = window
        self.program = program
        self.machine = Machine(program)
        self.disassembler = Disassembler(program, hex=False, color=False)

        self.h, self.w = self.window.getmaxyx()

    def run(self):
        self.window.clear()
        self.draw_instructions()
        self.window.refresh()

        self.window.getch()


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

    def run_debugger(window):
        debugger = Debugger(window, program)
        debugger.run()
        return debugger

    debugger = curses.wrapper(run_debugger)
    print(debugger.instructions)
