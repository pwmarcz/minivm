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
    def __init__(self, program):
        self.program = program
        self.machine = Machine(program)
        self.machine.use_io = False
        self.machine.on_input = self.input
        self.machine.start()

        dis = Disassembler(program, hex=False, color=False)
        self.instructions = list(dis.dump_lines())

    def init_curses(self):
        self.window = curses.initscr()
        self.h, self.w = self.window.getmaxyx()
        self.win_code = curses.newwin(self.h - 2, self.w // 2 - 1, 1, 0)
        self.win_frames = curses.newwin(
            self.h // 2, self.w // 2 - 1,
            1, self.w // 2,
        )
        self.win_output = curses.newwin(
            self.h // 2 - 3, self.w // 2 - 1,
            self.h // 2 + 2, self.w // 2
        )

        self.colors = Colors()
        curses.curs_set(0)

    def close_curses(self):
        curses.endwin()

    def input(self):
        self.close_curses()
        result = input('input: ')
        self.init_curses()
        return result

    def refresh(self):
        self.window.clear()
        self.draw_help()
        self.draw_code()
        self.draw_frames()
        self.draw_output()

        self.window.refresh()
        self.win_code.refresh()
        self.win_frames.refresh()
        self.win_output.refresh()

    def run(self):
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

    def draw_code(self):
        self.win_code.clear()
        h, w = self.win_code.getmaxyx()

        ip_line = None
        for i, (pos, line) in enumerate(self.instructions):
            if line and pos == self.machine.ip:
                ip_line = i

        start = max(0, (ip_line or 0) - h // 2)
        end = min(len(self.instructions), start + h)

        for i in range(start, end):
            y = i - start

            pos, line = self.instructions[i]
            if not line:
                continue

            prefix = '>' if i == ip_line else ' '
            self.win_code.addstr(y, 0, f'{prefix} {pos:04X}')
            self.win_code.addstr(y, 7, line[:w-8])
            attr = self.colors.REVERSE if i == ip_line else self.colors.NORMAL
            self.win_code.chgat(y, 0, w, attr)

    def draw_frames(self):
        self.win_frames.refresh()

        y = 0
        for frame in self.machine.frames:
            self.draw_frame_title(frame, y)
            y += 1
        self.draw_frame_details(self.machine.frames[-1], y)

    def draw_frame_title(self, frame, y):
        h, w = self.win_frames.getmaxyx()
        self.win_frames.addstr(y, 0, f'{frame.name} ({frame.ip:04X})')
        self.win_frames.chgat(y, 0, w, self.colors.BOLD)

    def draw_frame_details(self, frame, y):
        h, w = self.win_frames.getmaxyx()
        self.win_frames.addstr(y, 1, f'Locals ({len(frame.locals)}):', self.colors.DIM)
        y += 1
        for i, value in enumerate(frame.locals):
            self.win_frames.addstr(y, 2, f'{i:-2}: {dump_value(value)}'[:w-3])
            y += 1

        self.win_frames.addstr(y, 1, f'Stack ({len(frame.stack)}):', self.colors.DIM)
        y += 1
        start = max(0, len(frame.stack) - 8)
        for i in range(start, len(frame.stack)):
            prefix = '> ' if i == len(frame.stack) - 1 else '  '
            self.win_frames.addstr(y, 1, (prefix + dump_value(frame.stack[i]))[:w-2])
            y += 1

    def draw_help(self):
        y = self.h - 1
        self.window.addstr(y, 1, 'n - next instruction, q - quit', self.colors.DIM)

    def draw_output(self):
        output = self.machine.output

        self.win_output.clear()
        h, w = self.win_output.getmaxyx()

        lines = []
        for line in output.splitlines():
            if line == '':
                lines.append(line)
            else:
                while line:
                    line_part, line = line[:w], line[w:]
                    lines.append(line_part)

        start = max(0, len(lines) - h)
        for i in range(start, len(lines)):
            self.win_output.addstr(i - start, 0, lines[i])


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

    debugger = Debugger(program)
    try:
        debugger.init_curses()
        result = debugger.run()
    finally:
        debugger.close_curses()

    print(f'result: {dump_value(result)}')
