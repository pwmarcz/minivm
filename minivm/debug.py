import argparse
import sys
from pathlib import Path
import curses

from .tokens import dump_value
from .program import HEADER, Program
from .run import Machine
from .assemble import run_assembler
from .disassemble import Disassembler


class Colors:
    def __init__(self):
        curses.start_color()
        curses.use_default_colors()

        curses.init_pair(1, curses.COLOR_BLUE, -1)

        self.NORMAL = 0
        self.BOLD = curses.A_BOLD
        self.REVERSE = curses.A_REVERSE
        self.DIM = curses.color_pair(1) | curses.A_BOLD


class Debugger:
    def __init__(self, window, program):
        self.window = window
        self.program = program
        self.machine = Machine(program)
        self.machine.start()

        dis = Disassembler(program, hex=False, color=False)
        self.instructions = list(dis.dump_lines())

        self.h, self.w = self.window.getmaxyx()

        self.colors = Colors()

    def init_window(self):
        curses.curs_set(0)

    def refresh(self):
        self.window.clear()
        self.draw_help()
        self.draw_instructions()
        self.draw_frames()
        self.window.refresh()

    def run(self):
        self.init_window()
        while self.machine.running():
            self.refresh()
            c = self.window.getch()
            self.run_command(c)
        return self.machine.result

    def run_command(self, c):
        if c == ord('n'):
            self.machine.step()
        elif c == ord('q'):
            sys.exit(0)

    def draw_instructions(self):
        ip_line = None
        for i, (pos, line) in enumerate(self.instructions):
            if line and pos == self.machine.ip:
                ip_line = i

        w = self.w // 2
        h = self.h - 2
        start = max(0, (ip_line or 0) - h // 2)
        end = min(len(self.instructions), start + h)

        for i in range(start, end):
            y = i - start + 1

            pos, line = self.instructions[i]
            if not line:
                continue

            prefix = '>' if i == ip_line else ' '
            self.window.addstr(y, 0, f'{prefix} {pos:04X}')
            self.window.addstr(y, 7, line)
            attr = self.colors.REVERSE if i == ip_line else self.colors.NORMAL
            self.window.chgat(y, 0, w, attr)

    def draw_frames(self):
        y = 1
        for frame in self.machine.frames:
            self.draw_frame_title(frame, y)
            y += 1
        self.draw_frame_details(self.machine.frames[-1], y)

    def draw_frame_title(self, frame, y):
        x = self.w // 2 + 1
        w = self.w // 2 - 1
        self.window.addstr(y, x, f'{frame.name} ({frame.ip:04X})')
        self.window.chgat(y, x, w, self.colors.BOLD)

    def draw_frame_details(self, frame, y):
        x = self.w // 2 + 1
        # w = self.w // 2 - 1
        self.window.addstr(y, x, f'Locals ({len(frame.locals)}):', self.colors.DIM)
        y += 1
        for i, value in enumerate(frame.locals):
            self.window.addstr(y, x + 1, f'{i:-2}: {dump_value(value)}')
            y += 1

        self.window.addstr(y, x, f'Stack ({len(frame.stack)}):', self.colors.DIM)
        y += 1
        start = max(0, len(frame.stack) - 8)
        for i in range(start, len(frame.stack)):
            prefix = '> ' if i == len(frame.stack) - 1 else '  '
            self.window.addstr(y, x, prefix + dump_value(frame.stack[i]))
            y += 1

    def draw_help(self):
        y = self.h - 1
        self.window.addstr(y, 1, 'n - next instruction, q - quit', self.colors.DIM)


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
        return debugger.run()

    result = curses.wrapper(run_debugger)
    print('Result: ', result)
