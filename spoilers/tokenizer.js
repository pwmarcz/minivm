
class Tokenizer {
  constructor(text) {
    this.text = text;
    this.pos = 0;

    this.tokens = [];
  }

  current() {
    if (this.pos >= this.text.length) {
      return null;
    }
    return this.text.charAt(this.pos);
  }

  skipSpaces() {
    while (this.current() === ' ' || this.current() === '\n') {
      this.pos++;
    }
  }

  skipLine() {
    while (this.current() !== null && this.current() !== '\n') {
      this.pos++;
    }
  }

  handleNumber() {
    let s = '';
    while (/^\d$/.test(this.current())) {
      s += this.current();
      this.pos++;
    }
    return parseInt(s, 10);
  }

  run() {
    for (;;) {
      this.skipSpaces();

      const c = this.current();
      if (c === null) {
        return;
      }
      switch (c) {
        case '#':
          this.skipLine();
          break;

        case '+': case '-': case '*': case '/': case '(': case ')':
          this.tokens.push({type: c});
          this.pos++;
          break;

        default:
          if (/^\d$/.test(c)) {
            const n = this.handleNumber();
            this.tokens.push({type: 'NUMBER', value: n});
          } else {
            throw `unrecognized: ${c}`;
          }
          break;
      }
    }
  }
}

function tokenize(text) {
  const tokenizer = new Tokenizer(text);
  tokenizer.run();
  return tokenizer.tokens;
}

function test() {
  console.log(tokenize('2 * 2'));
  console.log(tokenize('2   *   2'));
  console.log(tokenize('2\n+\n2'));
  console.log(tokenize('#comment\n 2 + 2'));
}

test();
