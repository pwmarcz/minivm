
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

  run() {
    const tokens = [];

    for (;;) {
      this.skipSpaces();

      const c = this.current();
      if (c === null) {
        break;
      }

      throw `unrecognized: ${c}`;
    }
    return tokens;
  }
}


function test() {
  // {type: 'NUMBER', value: 2}, {type: '*'}, {type: 'NUMBER', value: 2}
  console.log(new Tokenizer('2 * 2').run());

  console.log(new Tokenizer('2   *   2').run());
  console.log(new Tokenizer('2\n+\n2').run());
  console.log(new Tokenizer('#comment\n 2 + 2').run());
}

test();


module.exports = { Tokenizer };
