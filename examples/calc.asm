FUNC "main" 0 1

    CONST_STRING "Calculator"
    CALL_VOID "println" 1

menu:
    # Print menu
    CONST_STRING ""
    CALL_VOID "println" 1
    CONST_STRING "0. Exit"
    CALL_VOID "println" 1
    CONST_STRING "1. Add two numbers"
    CALL_VOID "println" 1
    CONST_STRING "2. Add a list of numbers"
    CALL_VOID "println" 1

    # Read input
    CALL "input" 0
    STORE_LOCAL 0

    # Check if input is 0
    LOAD_LOCAL 0
    CONST_STRING "0"
    CMP_EQ
    JUMP_IF exit

    # Check if input is 1
    LOAD_LOCAL 0
    CONST_STRING "1"
    CMP_EQ
    JUMP_IF add_two

    # Check if input is 2
    LOAD_LOCAL 0
    CONST_STRING "2"
    CMP_EQ
    JUMP_IF add_list

    # If we got here, the input is unrecognized
    LOAD_LOCAL 0
    CONST_STRING "Unrecognized input!"
    CALL_VOID "println" 1
    JUMP menu

exit:
    RET

add_two:
    CALL "add_two" 0
    JUMP menu

add_list:
    CALL "add_list" 0
    JUMP menu

FUNC "add_two" 0 0
    # Read first number, convert
    CONST_STRING "First number: "
    CALL_VOID "print" 1
    CALL "input" 0
    CALL "to_int" 1

    # Read second number, convert
    CONST_STRING "Second number: "
    CALL_VOID "print" 1
    CALL "input" 0
    CALL "to_int" 1

    # Add numbers, display result
    OP_ADD
    CONST_STRING "Result: "
    CALL_VOID "print" 1
    CALL_VOID "println" 1
    RET

FUNC "add_list" 0 1
    # Local 0: sum
    CONST_INT 0
    STORE_LOCAL 0

add_sum_loop:
    # Read input
    CONST_STRING "Number (press ENTER to finish): "
    CALL_VOID "print" 1
    CALL "input" 0

    # Finish if input is empty
    DUP
    CONST_STRING ""
    CMP_EQ
    JUMP_IF add_sum_end

    # Convert to number, then add to sum
    CALL "to_int" 1
    LOAD_LOCAL 0
    OP_ADD
    STORE_LOCAL 0

    JUMP add_sum_loop

add_sum_end:
    DROP

    CONST_STRING "Result: "
    LOAD_LOCAL 0
    CALL "to_string" 1
    CALL "concat" 2
    CALL_VOID "println" 1
    RET
