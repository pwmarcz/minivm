# Starting code: read input, write to output.

from pathlib import Path
import argparse
import sys


HEADER = b'MINIVM\0\0'


def compile(s: str) -> bytearray:
    output = bytearray(b'')

    output += HEADER

    # Your compiler here

    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='input file, or -')
    parser.add_argument('output_file', help='output file, or -')

    args = parser.parse_args()

    if args.input_file == '-':
        input = sys.stdin.read()
    else:
        input = Path(args.input_file).read_text()

    output = compile(input)

    if args.output_file == '-':
        # use sys.stdout.buffer to write bytes
        sys.stdout.buffer.write(bytes(output))
    else:
        Path(args.output_file).write_bytes(output)


if __name__ == '__main__':
    main()
