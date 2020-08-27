# Bytecode format

The file starts with an 8-byte header:

    4D 49 4E 49 56 4D 00 00 = MINIVM\0\0

| Operation        | Code | Parameters                        | Effect                                                       |
| ---------------- | ---- | --------------------------------- | ------------------------------------------------------------ |
| `FUNC`           | 01   | `<name:string> <N:byte> <K:byte>` | Begin a new function with N params and K locals              |
| **Constants**    |      |                                   |                                                              |
| `CONST_NULL`     | 10   |                                   | Push `null` to stack                                         |
| `CONST_FALSE`    | 11   |                                   | Push `false` to stack                                        |
| `CONST_TRUE`     | 12   |                                   | Push `true` to stack                                         |
| `CONST_INT`      | 13   | `<byte>` (signed)                 | Push an integer to stack (-128..127)                         |
| `CONST_INT_BIG`  | 14   | `<byte>` x 4 (signed)             | Push an integer to stack (-2^31..2**31-1)                    |
| **Arithmetic**   |      |                                   |                                                              |
| `OP_NEG`         | 20   |                                   | `-a`                                                         |
| `OP_ADD`         | 21   |                                   | `a + b`                                                      |
| `OP_SUB`         | 22   |                                   | `a - b`                                                      |
| `OP_MUL`         | 23   |                                   | `a * b`                                                      |
| `OP_DIV`         | 24   |                                   | `a / b`                                                      |
| `OP_MOD`         | 25   |                                   | `a % b`                                                      |
| **Logic**        |      |                                   |                                                              |
| `OP_NOT`         | 28   |                                   | `!a`                                                         |
| `CMP_EQ`         | 30   |                                   | `a == b`                                                     |
| `CMP_NE`         | 31   |                                   | `a != b`                                                     |
| `CMP_LT`         | 32   |                                   | `a < b`                                                      |
| `CMP_LET`        | 33   |                                   | `a <= b`                                                     |
| `CMP_GT`         | 34   |                                   | `a > b`                                                      |
| `CMP_GTE`        | 35   |                                   | `a >= b`                                                     |
| **Stack/vars**   |      |                                   |                                                              |
| `DUP`            | 40   |                                   | Duplicate top value on stack                                 |
| `DROP`           | 41   |                                   | Remove top value from stack                                  |
| `LOAD_LOCAL`     | 4A   | `<N:byte>`                        | Push Nth local variable to stack                             |
| `STORE_LOCAL`    | 4B   | `<N:byte>`                        | Take a value from stack and store it in Nth local variable   |
| **Control flow** |      |                                   |                                                              |
| `CHECK`          | 50   |                                   | Take a value from stack, skip next instruction if false/null |
| `JUMP`           | 51   | `<N:byte>` (signed)               | Jump N bytes (+/-) from current instruction                  |
| `RET`            | 52   |                                   | Return from function, taking top value from stack            |
| `CALL`           | 53   | `<F:string> <N:byte>`             | Call function F, using N values from stack as arguments      |


The **string values** are ASCII strings, encoded with length as their first byte. Example:
* `FUNC "main" 0 2` -> `01 04 'm' 'a' 'i' 'n' 00 02`
* `CONST_STRING "hello"` -> `15 05 'h' 'e' 'l' 'l' 'o'`

The **integer values** for `CONST_INT` and `CONST_INT_BIG` are signed 8-bit and 32-bit integers. The encoding for 32-bit integers is little-endian.

Examples:
* `CONST_INT 42` = `CONST_INT $2A` -> `13 2A`
* `CONST_INT -1` -> `13 FF`
* `CONST_INT_BIG 51966` = `CONST_INT_BIG $CAFE` -> `14 FE CA 00 00`


(TODO explain conversion)
