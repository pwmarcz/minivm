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
