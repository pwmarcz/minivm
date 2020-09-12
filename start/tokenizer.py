class Tokenizer:
    def __init__(self, text):
        self.text = text
        self.pos = 0

        self.tokens = []

    def current(self):
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]

    def skip_spaces(self):
        while self.current() == ' ' and self.current() == '\n':
            self.pos += 1

    def run(self):
        tokens = []

        while True:
            self.skip_spaces()

            c = self.current()
            # ...

            raise Exception(f'unexpected: {c}')

        return tokens


def test():
    print(Tokenizer('2 + (2 * 2)').run())


if __name__ == '__main__':
    test()
