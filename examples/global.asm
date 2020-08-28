FUNC "main" 0 0
    CONST_STRING "hello"
    STORE_GLOBAL $FF
    LOAD_GLOBAL $FF
    CALL "print" 1
    RET
