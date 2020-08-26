import string
import unittest
import dataclasses
import re


STRING_ESCAPES = {
    '"': '"',
    "\\": "\\",
    "\n": "n",
    "\r": "r",
    "\t": "t",
}

STRING_UNESCAPES = dict((v, k) for k, v in STRING_ESCAPES.items())

STRING_ALLOWED = set(
    string.digits + string.ascii_letters + string.punctuation + string.whitespace
) - set(STRING_ESCAPES)


def escape_string(s):
    result = '"'
    for c in s:
        if c in STRING_ESCAPES:
            result += "\\" + STRING_ESCAPES[c]
        elif c in STRING_ALLOWED:
            result += c
        else:
            n = ord(c)
            assert n <= 255
            result += f"\\x{n:02x}"
    result += '"'
    return result


@dataclasses.dataclass
class Token:
    lineno: int
    col: int


@dataclasses.dataclass
class TLabel(Token):
    value: str

    def __str__(self):
        return self.value + ':'


@dataclasses.dataclass
class TIdent(Token):
    value: str

    def __str__(self):
        return self.value


@dataclasses.dataclass
class TInteger(Token):
    value: int

    def __str__(self):
        return str(self.value)


@dataclasses.dataclass
class TString(Token):
    value: str

    def __str__(self):
        return escape_string(self.value)


class ParseError(Exception):
    def __init__(self, lineno, col, message):
        self.lineno = lineno
        self.col = col
        self.message = message

    def __str__(self):
        return f"{self.lineno}: {self.message}"


class Scanner:
    def __init__(self, line, lineno):
        self.line = line
        self.lineno = lineno
        self.col = 0

    def end(self):
        return self.col == len(self.line)

    def current(self):
        if self.col == len(self.line):
            return None
        return self.line[self.col]

    def scan_ws(self):
        while not self.end() and self.current() in " \t":
            self.col += 1
        if self.current() == "#":
            self.col = len(self.line)

    def error(self, message):
        raise ParseError(self.lineno, self.col, message)

    def scan_regex(self, regex, name):
        m = re.match(regex, self.line[self.col :])
        if not m:
            self.error(f"expecting {name}")
        result = m.group(0)
        col = self.col
        self.col += len(result)
        return col, result

    def scan_string(self):
        result = ""
        col = self.col
        self.col += 1
        while True:
            current = self.current()
            if current is None:
                self.error("unterminated string literal")
            elif current in STRING_ALLOWED:
                result += current
                self.col += 1
            elif current == "\\":
                self.col += 1
                current = self.current()
                if current is None:
                    self.error("unterminated escape sequence")
                elif current in STRING_UNESCAPES:
                    result += STRING_UNESCAPES[current]
                    self.col += 1
                elif current == "x":
                    _col, s = self.scan_regex("x[a-fA-F0-9]{2}", "hex escape sequence")
                    n = int(s[1:], 16)
                    result += chr(n)
                else:
                    self.error("unknown escape sequence")
            elif current == '"':
                self.col += 1
                return col, result
            else:
                self.error("unknown character in string literal")

    def scan(self):
        self.scan_ws()
        if self.end():
            return None

        current = self.current()
        if current in string.ascii_letters:
            col, s = self.scan_regex(r"[a-zA-Z0-9_]+", "identifier")
            if self.current() == ':':
                self.col += 1
                return TLabel(self.lineno, col, s)
            return TIdent(self.lineno, col, s)
        elif current in string.digits or current == "-":
            col, s = self.scan_regex(r"-?[0-9]+", "number")
            return TInteger(self.lineno, col, int(s))
        elif current == "$":
            col, s = self.scan_regex(r"\$-?[0-9a-fA-F]+", "hex number")
            return TInteger(self.lineno, col, int(s[1:], 16))
        elif current == '"':
            col, s = self.scan_string()
            return TString(self.lineno, col, s)
        else:
            self.error("unexpected character")

    def iter(self):
        while True:
            token = self.scan()
            if token:
                yield token
            else:
                break


class TokensTest(unittest.TestCase):
    def test_escape_string(self):
        s = 'hello \n world"'
        self.assertEqual(escape_string(s), '"hello \\n world\\""')
        s = 'hello \x01 world'
        self.assertEqual(escape_string(s), '"hello \\x01 world"')

    def scan(self, line):
        t = Scanner(line, 0)
        return list(t.iter())

    def test_tokenize(self):
        self.assertListEqual(self.scan(''), [])
        self.assertListEqual(self.scan('# comment'), [])
        self.assertListEqual(self.scan('hello # comment'), [
            TIdent(0, 0, 'hello')
        ])
        self.assertListEqual(self.scan('foo: bar -123 $FF'), [
            TLabel(0, 0, 'foo'),
            TIdent(0, 5, 'bar'),
            TInteger(0, 9, -123),
            TInteger(0, 14, 255),
        ])

    def test_tokenize_string(self):
        self.assertListEqual(self.scan('"hello \\n world\\""'), [
            TString(0, 0, 'hello \n world"')
        ])
        self.assertListEqual(self.scan('"hello \\x01 world"'), [
            TString(0, 0, 'hello \x01 world')
        ])
