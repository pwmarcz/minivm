# MiniVM reference manual

- [MiniVM reference manual](#minivm-reference-manual)
  - [Summary](#summary)
  - [Commands](#commands)
  - [MiniVM assembly syntax](#minivm-assembly-syntax)
  - [Data types](#data-types)
  - [Stack](#stack)
  - [Functions and frames](#functions-and-frames)
  - [Control flow](#control-flow)
  - [Built-in functions](#built-in-functions)
  - [All operations](#all-operations)
  - [Bytecode format](#bytecode-format)

## Summary

* Assembly compiled to bytecode
* Stack-based virtual machine
* Each function has a separate frame with its own stack
* Frame contains local variables; the arguments are passed as local variables
* For control flow, there is `JUMP` and `JUMP_IF`

## Commands

* `mini run`: run a program (from source, or from bytecode):

      ./mini run program.asm
      ./mini run program.bc

* `mini assemble` (or `as`): compile a program to bytecode:

      mini as program.asm program.bc

* `mini disasseble` (or `dis): decompile a program:

      mini dis progran.bc

## MiniVM assembly syntax

Instructions are written one per line:

    CONST_INT 2
    CONST_INT 3

Comments start with `#`:

    # comment 1
    OP_ADD  # comment 2

Use `$` for hexadecimal numbers:

    CONST_INT_BIG $FFFF

Use `label:` for labels:

    LOOP:
        JUMP LOOP

## Data types

Programs operate on the following values. They can be stored on stack and in variables.

* **null**
* **boolean** - True and False
* **int** - 16-bit signed integers (between -0x8000 and 0x7FFF)
* **string**

## Stack

The instructions operate on a stack:

| Comment              | Instruction   | Stack |
| -------------------- | ------------- | ----- |
| push 2               | `CONST_INT 2` | 2     |
| push 3               | `CONST_INT 3` | 2 3   |
| add two numbers      | `OP_ADD`      | 5     |
| push 4               | `CONST_INT 4` | 5 4   |
| multiply two numbers | `OP_MUL`      | 20    |

## Functions and frames

Functions are declared as follows:

    FUNC "name" <num_args> <num_vars>

Entering a function creates a new *frame*, with a separate stack, and `num_args + num_vars` local variables. You can use `LOAD_LOCAL` and `STORE_LOCAL` to access them.

To exit a function, use `RET`. It will take the result from the local stack, remove the frame, and push the result on calling function's stack.

At the beginning, the function `main` is called, with no arguments.

The following program (`examples/locals.asm`):

    FUNC "main" 0 1
        # Store "local" in local 0
        CONST_STRING "local"
        STORE_LOCAL 0

        CONST_INT 0

        # Call "add3" on 3 values
        CONST_INT 1
        CONST_INT 2
        CONST_INT 3
        CALL "add3" 3

        OP_ADD
        RET

    FUNC "add3" 3 0
        LOAD_LOCAL 0
        LOAD_LOCAL 1
        OP_ADD
        LOAD_LOCAL 2
        OP_ADD
        RET

Will execute like this:

| Function | Instruction            | Stack 1 | Locals 1 | Stack 2 | Locals 2 |
| -------- | ---------------------- | ------- | -------- | ------- | -------- |
| main     | `CONST_STRING "local"` | "local" | null     |         |          |
| main     | `STORE_LOCAL 0`        |         | "local"  |         |          |
| main     | `CONST_INT 0`          | 0       | "local"  |         |          |
| main     | `CONST_INT 1`          | 0 1     | "local"  |         |          |
| main     | `CONST_INT 2`          | 0 1 2   | "local"  |         |          |
| main     | `CONST_INT 3`          | 0 1 2 3 | "local"  |         |          |
| main     | `CALL "add3" 3`        | 0       | "local"  |         | 1 2 3    |
| add3     | `LOAD_LOCAL 0`         | 0       | "local"  | 1       | 1 2 3    |
| add3     | `LOAD_LOCAL 1`         | 0       | "local"  | 1 2     | 1 2 3    |
| add3     | `OP_ADD`               | 0       | "local"  | 3       | 1 2 3    |
| add3     | `LOAD_LOCAL 2`         | 0       | "local"  | 3 3     | 1 2 3    |
| add3     | `OP_ADD`               | 0       | "local"  | 6       | 1 2 3    |
| add3     | `RET`                  | 0 6     | "local"  |         |          |
| main     | `OP_ADD`               | 6       | "local"  |         |          |
| main     | `RET`                  |         |          |         |          |

## Control flow

For control flow, you can use:
* Comparison operators (`CMP_EQ` etc.) - they will return true or false
* `JUMP` to jump to a label
* `JUMP_IF` to jump to a label if a condition is true

You can add label to any line by prepending it with label name and colon at the beginning.

Example program (`examples/sum.asm`):

    FUNC "main" 0 2
        # Compute a sum from 0 to 10:

        # Local 0 = sum
        CONST_INT 0
        STORE_LOCAL 0

        # Local 1 = index
        CONST_INT 1
        STORE_LOCAL 1

    LOOP:
        # Check if index == 10, jump to end if true
        LOAD_LOCAL 1
        CONST_INT 10
        CMP_EQ
        JUMP_IF END

        # sum = sum + index
        LOAD_LOCAL 0
        LOAD_LOCAL 1
        OP_ADD
        STORE_LOCAL 0

        # index = index + 1
        LOAD_LOCAL 1
        CONST_INT 1
        OP_ADD
        STORE_LOCAL 1

        JUMP LOOP

    END:
        # Return sum
        LOAD_LOCAL 0
        RET

## Built-in functions

The following functions are available to the program, without defining them. Make sure to call them with correct number of arguments.

* `print(x)` - print a value to standard output (without newline)
* `println(x)` - print a value to standard output (with newline)
* `input()` - read a string from standard input
* `to_int(s)` - convert a string to int
* `to_string(x)` - convert a value to string
* `concat(s1, s2)` - concatenate two strings
* `length(s)` - compute length of a string
* `slice(s, pos, length)` - return a substring starting from `pos` and `length` characters long

## All operations

See also "Bytecode format" below, for how the operations are encoded.

* `FUNC "name" n k`

  Declare a function with `n` arguments and `k` additional variables.

* `CALL "name" n`

  Call a function with given name and `n` arguments. `n` must be the same as in function declaration.

  This will remove `n` values from the stack, create a new frame, and store the arguments and `n` first locals in that frame. The additional locals will be `null`.

  For example, if a function is declared as `FUNC "foo" 2 2`, and called like this:

      CONST_INT 10
      CONST_INT 15
      CALL "foo" 2

  Then the local variables in the new frame will be `10 15 null null`.

* `CALL_VOID "name" n`

  Same as `CALL`, but after returning, the function result will not be pushed to stack.

* `RET`

  Return to previous function. This will remove the current frame, but use the top-most value from stack as a result. The result will be pushed to stack in previous frame.

  If the stack is empty, the result will be `null`.

* `CONST_NULL`: Push `null` to stack.
* `CONST_FALSE`: Push `false` to stack.
* `CONST_TRUE`: Push `true` to stack.
* `CONST_INT n`, `CONST_INT_BIG n`

  Push an integer N to stack. The value for `CONST_INT` must be in the range `-0x80..0x7F`, and the value for `CONST_INT_BIG` must be between `-0x8000..0x7FFF`.

* `CONST_STRING "string"`

  Push a string value to stack.

* `OP_NEG`

  Replace a number `a` on stack with `-a`.

* `OP_ADD`, `OP_SUB`, `OP_MUL`, `OP_DIV`, `OP_MOD`

  Remove two numbers (`a`, `b`) from the stack, and push a result:

  * `OP_ADD`: `a + b`
  * `OP_SUB`: `a - b`
  * `OP_MUL`: `a * b`
  * `OP_DIV`: `a // b` (integer division)
  * `OP_MOD`: `a % b` (modulo)

* `OP_NOT`

  Replace a value to stack with its logical negation:

  * `true` if the value was null/false/0/empty string,
  * `false` otherwise.

* `CMP_EQ`, `CMP_NE`, `CMP_LT`, `CMP_LTE`, `CMP_GT`, `CMP_GTE`

  Remove two values (`a`, `b`) from the stack, and push a comparison result (true or false):

  * `CMP_EQ`: `a == b`
  * `CMP_NE`: `a != b`
  * `CMP_LT`: `a < b`
  * `CMP_LTE`: `a <= b`
  * `CMP_GT`: `a > b`
  * `CMP_GTE`: `a >= b`

* `DUP`: Duplicate top value on stack.

* `DROP`: Remove top value from stack.

* `LOAD_GLOBAL "name"`

  Push a global variable called `name` to stack. The variable needs to be initialized using `STORE_GLOBAL` first.

* `STORE_GLOBAL "name"`

  Remove a value from stack, and store it in global variable called `name`.

* `LOAD_LOCAL n`

  Push a local variable number `n` to stack. In a function declared as `FUNC "name" n k`, the first `n` local variables contain function arguments.

* `STORE_LOCAL n`

  Remove a value from stack, and store it in local variable number `n`.

* `JUMP label`

  Jump to label `label` (instruction marked with `label:`).

  Internally, the jump will be stored as byte offset relative to current instruction (for instance, +5 bytes, or -10 bytes). The offset is encoded in 2 bytes, and must be between `-0x8000` and `0x7FFF`.

* `JUMP_IF label`

  Same as `JUMP label`, but first removes a value from the stack, and jumps only if it's not falsy (`false`, `null` or `0`).

## Bytecode format

The file starts with an 8-byte header:

    4D 49 4E 49 56 4D 00 00 = MINIVM\0\0

The operations are encoded as follows:

| Operation        | Code | Parameters                        | Effect                                                         |
| ---------------- | ---- | --------------------------------- | -------------------------------------------------------------- |
| `FUNC`           | 01   | `<name:string> <n:byte> <k:byte>` | Begin a function `name` with `n` params and `k` locals         |
| **Constants**    |      |                                   |                                                                |
| `CONST_NULL`     | 10   |                                   | Push `null` to stack                                           |
| `CONST_FALSE`    | 11   |                                   | Push `false` to stack                                          |
| `CONST_TRUE`     | 12   |                                   | Push `true` to stack                                           |
| `CONST_INT`      | 13   | `<n:byte>` (signed)               | Push an integer to stack (`-0x80 <= n <= 0x7F`)                |
| `CONST_INT_BIG`  | 14   | `<nl:byte>` `<nh:byte>` (signed)  | Push an integer to stack (`-0x8000 <= n <= 0x7FFF`)            |
| **Arithmetic**   |      |                                   |                                                                |
| `OP_NEG`         | 20   |                                   | `-a`                                                           |
| `OP_ADD`         | 21   |                                   | `a + b`                                                        |
| `OP_SUB`         | 22   |                                   | `a - b`                                                        |
| `OP_MUL`         | 23   |                                   | `a * b`                                                        |
| `OP_DIV`         | 24   |                                   | `a // b` (integer)                                             |
| `OP_MOD`         | 25   |                                   | `a % b`                                                        |
| **Logic**        |      |                                   |                                                                |
| `OP_NOT`         | 28   |                                   | `!a`                                                           |
| `CMP_EQ`         | 30   |                                   | `a == b`                                                       |
| `CMP_NE`         | 31   |                                   | `a != b`                                                       |
| `CMP_LT`         | 32   |                                   | `a < b`                                                        |
| `CMP_LET`        | 33   |                                   | `a <= b`                                                       |
| `CMP_GT`         | 34   |                                   | `a > b`                                                        |
| `CMP_GTE`        | 35   |                                   | `a >= b`                                                       |
| **Stack/vars**   |      |                                   |                                                                |
| `DUP`            | 40   |                                   | Duplicate top value on stack                                   |
| `DROP`           | 41   |                                   | Remove top value from stack                                    |
| `LOAD_GLOBAL`    | 48   | `<n:byte>`                        | Push `n`-th global variable to stack                           |
| `STORE_GLOBAL`   | 49   | `<n:byte>`                        | Take a value from stack and store it in `n`-th global variable |
| `LOAD_LOCAL`     | 4A   | `<n:byte>`                        | Push `n`-th local variable to stack                            |
| `STORE_LOCAL`    | 4B   | `<n:byte>`                        | Take a value from stack and store it in `n`-th local variable  |
| **Control flow** |      |                                   |                                                                |
| `JUMP`           | 50   | `<nl:byte>` `<nh:byte>` (signed)  | Jump `n` bytes (+/-) from current instruction                  |
| `JUMP_IF`        | 51   | `<nl:byte>` `<nh:byte>` (signed)  | Take a value from stack, jump `n` bytes if not false           |
| `RET`            | 58   |                                   | Return from function, taking top value from stack              |
| `CALL`           | 59   | `<name:string> <n:byte>`          | Call function `name`, using `n` values from stack as arguments |
| `CALL_VOID`      | 5A   | `<name:string> <n:byte>`          | Same as `CALL`, but do not put the result on stack             |


The **string values** are ASCII strings, encoded with length as their first byte. Examples:
* `FUNC "main" 0 2` -> `01 04 'm' 'a' 'i' 'n' 00 02`
* `CONST_STRING "hello"` -> `15 05 'h' 'e' 'l' 'l' 'o'`

The numbers of `CONST_INT_BIG` and `JUMP*` are signed 16-bit (2-byte values). The encoding is little-endian (lower byte first).

Examples:
* `CONST_INT 42` = `CONST_INT $2A` -> `13 2A`
* `CONST_INT_BIG 51966` = `CONST_INT_BIG $CAFE` -> `14 FE CA`
* `JUMP 16` = `JUMP $10` -> `51 10 00`
* `JUMP -1` -> `51 FF FF`
