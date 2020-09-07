FUNC "main" 0 0
    CONST_STRING "hello"
    STORE_GLOBAL "greeting"
    LOAD_GLOBAL "greeting"
    CALL "print" 1
    RET
