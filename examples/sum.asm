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
