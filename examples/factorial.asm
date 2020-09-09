FUNC "main" 0 2
    CONST_INT 5
    CALL "factorial" 1
    CALL "print" 1
    RET

FUNC "factorial" 1 1
    CONST_INT 1
    STORE_LOCAL 1

LOOP:
    LOAD_LOCAL 0
    CONST_INT 1
    CMP_LTE
    JUMP_IF END

    LOAD_LOCAL 0
    LOAD_LOCAL 1
    OP_MUL
    STORE_LOCAL 1

    LOAD_LOCAL 0
    CONST_INT 1
    OP_SUB
    STORE_LOCAL 0

    JUMP LOOP

END:
    LOAD_LOCAL 1
    RET
