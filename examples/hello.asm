FUNC "main" 0 0
    # Print message
    CONST_STRING "What is your name? "
    CALL_VOID "print" 1

    # Read input
    CALL "input" 0

    # Call "greet" with input data
    CALL_VOID "greet" 1
    RET

FUNC "greet" 1 0

    # Compute: "Hello, " + name
    CONST_STRING "Hello, "
    LOAD_LOCAL 0
    CALL "concat" 2

    # Compute: ... + "!"
    CONST_STRING "!"
    CALL "concat" 2

    # Print the result
    CALL_VOID "println" 1
    RET
