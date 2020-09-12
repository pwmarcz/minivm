/*
  A skeleton code for parser.

  Start with the following grammar:

    expression = term (('+' | '-' | '*' | '/') term)+
    term = NUMBER

*/

class Parser {
  constructor(text) {
    const Tokenizer = require('./tokenizer.js').Tokenizer;

    this.tokens = new Tokenizer(text).run();
    this.pos = 0;
  }

  /* Parse an expression, return something like '(((A + B) + C) - D)' */
  parseExpression() {
    // 1. parse term
    // 2. loop:
    //    2a. parse operator (+ - * /)
    //    2b. parse term, combine with previous
    return result;
  }

  /* Parse a term, return something like 'number(123)' */
  parseTerm() {
    // check if current token is a number
    // advance position, return
  }
}

function test() {
  console.log(new Parser('1').parseNumber());
  /*
  console.log(new Parser('1 - 2 + 3').parseExpression());
  console.log(new Parser('2 + 2 * 2').parseExpression());
  console.log(new Parser('(2 + 2) * 2').parseExpression());
  */
}

test();
