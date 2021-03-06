## Intro

* Schedule (lunch break?)
* Workshop plan
* This is very experimental, so not sure how much we'll manage do
* Not sure about the starting samples - they might be not useful enough, or *too* useful
* If it's interesting, we can continue another time

## What is compiling

* Computer (von Neumann architecture) - a simple diagram:
  * memory
  * program (and PC)
  * registers (for example, A, X, Y)
  * stack (and SP)

* How does a compiled program look like?

  Use [Compiler Explorer](https://godbolt.org/). Look at a simple program:
  ```
  int factorial(int n) {
    int a = 1;
    for (int i = 1; i <= n; i++) {
        a *= i;
    }
    return a;
  }
  ```
  * Expand the `for` into a `while`
  * Explain what every line does
  * Try gcc with -O0, with -O1
  * For fun: try clang with -O1, then -O2 ()
  * Enable "compile to binary" to show instructions are encoded as bytes

* What does a compiler do? What parts does it translate?
  * Source code -> machine instructions (bytes)
  * Named variables -> places in memory
  * Structured programming (for loops, etc.) -> jumps (goto)
  * Structured memory (strings, maps etc.) -> raw bytes

* Simpler model: a virtual machine, operating on bytecode
  * Usually: a stack frame, local variables
  * Show the above example but with WebAssembly
  * Show Python
  * [Java bytecode](https://en.wikipedia.org/wiki/Java_bytecode#Example)

* (Maybe also show LLVM IR, to show it's not stack)

## Stack machines

* [Reverse Polish notation](https://en.wikipedia.org/wiki/Reverse_Polish_notation)
* A way of writing without brackets, but also, can be thought of as a stack
* Try to translate simple expressions into RPN:
  * `2 + 3 * 4`
  * `(2 + 3) * 4`
  * `2 * (a + b + c + d)`
  * `sqrt(x^2 + y^2)`
  * `print("Hello, it's " + int(hour) + "!")`
* Aside: if you want to see a programming language that does this, check out Forth

## MiniVM

* Program: Hello world
  * Run directly
  * Compile and run, disassable
  * Show debugger
* More complicated example: sum
* Exercise: calculator (sum, sum of N)
  * add average ((a+b)/2)
  * add average of N
  * add sqrt (try multiplying 1*1, 2*2, 3*3 etc. until the number is bigger than N)
* Exercise: password checker (as binary) -> palindrome
  * Disassemble (or run in debugger), check what would be a good password
  * Try "cracking" the program so that any password works, or it doesn't as for password at all
  * Easy mode: decompile, modify source, compile
  * Hard mode: use a hex editor! (hexedit, ghex, ...)

## Writing first compiler

Compile "Forth-like" expressions like "2 2 + 3 *".

You can use the start code (`start/compiler.js` / `start/compiler.py`).

## Theory: tokenizing and parsing

* Draw compiler passes:
  * source code
  * (tokenize) -> tokens
  * (parse) -> AST
  * (typecheck, translate) -> IR
  * (optimize, generate code) -> ASM
  * (assemble) -> machine code

* Our pipeline will be much simpler:
  * source code
  * (tokenize) -> tokens
  * (parse, translate, generate code) -> ASM or machine code

* Sometimes, even a simple pass! (see [Turbo Pascal](https://prog21.dadgum.com/47.html))

## Writing a tokenizer

* Tokenizer (lexer): show example tokens, such as `2 * (a + b + c + d)`
* Disregard comments (for example, everything from `#` to newline)
* Disregard whitespace (space, tab, newline)
* Decide based on at first character.
* Or use regexes!

We will need:
* integer numbers (type: `NUMBER`, value: `123`)
* special (type: `+`, `-` etc.). At least the following:
  ```
  ( )
  + - * /
  ```
* bonus: identifiers (type: `IDENT`, value: `"hello"`)

* Exercise: finish a tokenizer (or write own from start)

## Parsing

* Usually start the language with defining a grammar
* Can use a *parser generator*, or write our own (recursive descent parser)
* Surprisingly, a lot of engines roll their own
* Grammar that we want (more or less):
  ```
  expression = NUMBER
             | '(' expression ')'
             | expression '+' expression
             | expression '-' expression
             | expression '*' expression
             | expression '/' expression
  ```
* What are problems with this grammar?
  * Ambiguous
  * Left-recursive
  * Cannot immediately decide which rule to follow
* Start with this:
  ```
  expression = term (('+' | '-' | '*' | '/') term)+
  term = NUMBER
  ```

  (yes, it will not handle correct precedence)
* Next step: add parentheses:
  ```
  term = NUMBER | '(' expression ')'
  ```
* At first, it will just print something (indented debugging info)
* Make it generate code!

## Adding precedence

Can be done here, or earlier:

```
expression = term (('+' | '-') term)+
term = factor (('*' | '/') factor)+
factor = NUMBER | '(' expression ')'
```

## Variables

Introduce statements: variable declaration, assignments

## Control structures

Add "if" and "while"

## Where to go from there?

* Crafting Interpreters
* Zachtronics games!
