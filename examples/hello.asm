FUNC "main" 0 0
    CONST_STRING "What is your name? "
    CALL_VOID "print" 1
    CALL "input" 0
    CALL_VOID "greet" 1
    RET

FUNC "greet" 1 0
    CONST_STRING "Hello, "
    LOAD_LOCAL 0
    CALL "concat" 2
    CONST_STRING "!"
    CALL "concat" 2
    CALL_VOID "println" 1
    RET
