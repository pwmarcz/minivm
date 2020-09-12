
class Tokenizer {
  constructor(text) {
    this.text = text;
    this.pos = 0;
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
    const tokens = [];

    for (;;) {
      this.skipSpaces();

      const c = this.current();
      if (c === null) {
        break;
      }
      switch (c) {
        case '#':
          this.skipLine();
          break;

        case '+': case '-': case '*': case '/': case '(': case ')':
          tokens.push({type: c});
          this.pos++;
          break;

        default:
          if (/^\d$/.test(c)) {
            const n = this.handleNumber();
            tokens.push({type: 'NUMBER', value: n});
          } else {
            throw `unrecognized: ${c}`;
          }
          break;
      }
    }

    return tokens;
  }
}

function test() {
  console.log(new Tokenizer('2 * 2').run());
  console.log(new Tokenizer('2   *   2').run());
  console.log(new Tokenizer('2\n+\n2').run());
  console.log(new Tokenizer('#comment\n 2 + 2').run());
}

test();

module.exports = {Tokenizer};
