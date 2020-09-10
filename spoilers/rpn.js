// Simple RPN compiler.

// npm install rw
const rw = require('rw');


const Op = {
  FUNC: 0x01,

  CONST_INT: 0x13,

  OP_ADD: 0x21,
  OP_SUB: 0x22,
  OP_MUL: 0x23,
  OP_DIV: 0x24,

  RET: 0x58,
}


function toBytes(text) {
  return Array.from(Buffer.from(text));
}


const HEADER = toBytes('MINIVM\0\0');


class Program {
  constructor() {
    this.output = [];
  }

  emit(data) {
    if (Array.isArray(data)) {
      this.output.push(...data);
    } else {
      this.output.push(data);
    }
  }

  emitString(string) {
    const bytes = toBytes(string);
    this.emit(bytes.length);
    this.emit(bytes);
  }
}


function compile(input) {
  const program = new Program();

  program.emit(HEADER);
  program.emit(Op.FUNC);
  program.emitString('main');
  program.emit(0);
  program.emit(0);

  input = input.trim();
  const parts = input.split(' ');

  for (const part of parts) {
    switch (part) {
      case '+':
        program.emit(Op.OP_ADD);
        break;
      case '-':
        program.emit(Op.OP_SUB);
        break;
      case '/':
        program.emit(Op.OP_DIV);
        break;
      case '*':
        program.emit(Op.OP_MUL);
        break;

      case '':
        break;

      default: {
        if(/^[0-9]+/.test(part)) {
          const num = parseInt(part, 10);
          if (!(0 <= num && num < 127)) {
            throw `number too big: ${num}`;
          }
          program.emit([Op.CONST_INT, num]);
        } else {
          throw `unrecognized: ${part}`;
        }
      }
    }
  }
  program.emit(Op.RET);

  return program.output;
}


function main() {
  const args = process.argv.slice(2);

  if (args.length != 2) {
    const split = process.argv[1].split('/');
    const prog = split[split.length - 1];
    console.log(`Usage: node ${prog} input output`);
    console.log('(use - for stdin/stdout)')
    process.exit(1);
  }

  const [inputFile, outputFile] = args;
  const input = rw.dash.readFileSync(inputFile, 'utf8');
  const output = compile(input);
  rw.dash.writeFileSync(outputFile, Buffer.from(output));
}

main();
