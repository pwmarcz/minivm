# Bytecode format

TODO header

| Operation       | Code | Parameters                        | Effect                                                       |
| --------------- | ---- | --------------------------------- | ------------------------------------------------------------ |
| `FUNC`          | 00   | `<name:string> <N:byte> <K:byte>` | Begin a new function with N params and K locals              |
| `CONST_NULL`    | 10   |                                   | Push `null` to stack                                         |
| `CONST_FALSE`   | 11   |                                   | Push `false` to stack                                        |
| `CONST_TRUE`    | 12   |                                   | Push `true` to stack                                         |
| `CONST_INT`     | 13   | `<byte>`                          | Push an integer to stack (-128..127)                         |
| `CONST_INT_BIG` | 14   | `<byte>` x 4                      | Push an integer to stack (-2^31..2**31-1)                    |
| `OP_NEG`        | 20   |                                   | `-a`                                                         |
| `OP_ADD`        | 21   |                                   | `a + b`                                                      |
| `OP_SUB`        | 22   |                                   | `a - b`                                                      |
| `OP_MUL`        | 23   |                                   | `a * b`                                                      |
| `OP_DIV`        | 24   |                                   | `a / b`                                                      |
| `OP_MOD`        | 25   |                                   | `a % b`                                                      |
| `OP_NOT`        | 28   |                                   | `!a`                                                         |
| `OP_AND`        | 29   |                                   | `a && b`                                                     |
| `OP_OR`         | 2A   |                                   | `a || b`                                                     |
| `CMP_EQ`        | 30   |                                   | `a == b`                                                     |
| `CMP_NE`        | 31   |                                   | `a != b`                                                     |
| `CMP_LT`        | 32   |                                   | `a < b`                                                      |
| `CMP_LET`       | 33   |                                   | `a <= b`                                                     |
| `CMP_GT`        | 34   |                                   | `a > b`                                                      |
| `CMP_GTE`       | 35   |                                   | `a >= b`                                                     |
| `DUP`           | 40   |                                   | Duplicate top value on stack                                 |
| `DROP`          | 41   |                                   | Remove top value from stack                                  |
| `LOAD_LOCAL`    | 4A   | `<N:byte>`                        | Push Nth local variable (with a given number) to stack       |
| `STORE_LOCAL`   | 4B   | `<N:byte>`                        | Take a value from stack and store it in Nth local variable   |
| `CHECK`         | 50   |                                   | Take a value from stack, skip next instruction if false/null |
| `JUMP`          | 51   | `<N:byte>`                        | Jump N bytes (can be positive or negative)                   |
| `RET`           | 52   |                                   | Return from function, taking top value from stack            |
| `CALL`          | 53   | `<F:string> <N:byte>`             | Call function F, using N values from stack as arguments      |


The **string values** are ASCII strings, encoded with length as their first byte. Example:
* "hello" -> `05 'h' 'e' 'l' 'l' 'o'`

The **integer values** for `CONST_INT` and `CONST_INT_BIG` are signed 8-bit and 32-bit integers. Note that even though `CONST_INT` carries an 8-bit value, intenally the VM will operate on 32-bit values.

The encoding for 32-bit integers is little-endian. Examples:
* 51966 = `0xCAFE` is encoded as `FE CA 00 00`
* -1 is encoded as `FF FF FF FF`

(TODO explain conversion)
