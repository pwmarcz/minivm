FUNC "main" 0 0
    CONST_STRING "Enter password: "
    CALL_VOID "print" 1
    CALL "input" 0
    CALL "ck" 1
    JUMP_IF good

    CONST_STRING "Incorrect password!"
    CALL_VOID "println" 1
    RET
good:
    CALL_VOID "cong" 0
    RET

FUNC "ck" 1 2
    LOAD_LOCAL 0
    CALL "length" 1
    DUP
    STORE_LOCAL 1

    CONST_INT 5
    CMP_LT
    JUMP_IF incorrect

    CONST_INT 0
    STORE_LOCAL 2

loop:
    # s[i]
    LOAD_LOCAL 0
    LOAD_LOCAL 2
    CONST_INT 1
    CALL "slice" 3

    # s[length - i - 1]
    LOAD_LOCAL 0
    LOAD_LOCAL 1
    LOAD_LOCAL 2
    OP_SUB
    CONST_INT 1
    OP_SUB
    CONST_INT 1
    CALL "slice" 3

    CMP_NE
    JUMP_IF incorrect

    LOAD_LOCAL 2
    CONST_INT 1
    OP_ADD
    DUP
    STORE_LOCAL 2

    LOAD_LOCAL 1
    CMP_LT
    JUMP_IF LOOP

    CONST_TRUE
    RET

incorrect:
    CONST_FALSE
    RET

FUNC "cong" 0 0
    CONST_STRING "IF9fX19fX19fX19fX19fX19fXyAKPCBDb25ncmF0dWxhdGlvbnMhID4KIC0tLS0tLS0tLS0tLS0tLS0tLSAKICAgICAgICBcICAgXl9fXgogICAgICAgICBcICAob28pXF9fX19fX18KICAgICAgICAgICAgKF9fKVwgICAgICAgKVwvXAogICAgICAgICAgICAgICAgfHwtLS0tdyB8CiAgICAgICAgICAgICAgICB8fCAgICAgfHwK"
    CALL "b64d" 1
    CALL_VOID "print" 1
    RET
