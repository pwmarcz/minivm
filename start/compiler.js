// Starting code: read input, write to output.

// npm install rw
const rw = require('rw');


function toBytes(text) {
  return Array.from(Buffer.from(text));
}

const HEADER = toBytes('MINIVM\0\0');


function compile(input) {
  const output = [];

  output.push(...HEADER);

  // Your compiler here

  return output;
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
