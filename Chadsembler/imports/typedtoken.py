"""
Module containing the 'TypedToken' class that inherits from the 'UntypedToken' class
"""

from untypedtoken import UntypedToken

class TypedToken(UntypedToken):
    """
    -Class encapsulating all token related data, including a token type
    -A TypedToken can be created by giving an UntypedToken a Type
        therefore making it suitable to inherit from UntypedToken
    -Token types are available as static member which will be used by the Lexer class
    """

    # --Static Members (Belong to the class and not an individual class instance)
    END: int = 0  # /
    INSTRUCTION: int = 1  # INP, OUT, ADD, etc.
    ADDRESSING_MODE: int = 2  # IMMEDIATE, REGISTER, #, %, etc.
    VALUE: int = 3  # Any integer value (E.g. 5, 200, -100, etc.)
    REGISTER: int = 4  # ACC, IP, etc.
    LABEL: int = 5  # Any valid label (E.g. NUM, FUNC, etc.)
    SEPERATOR: int = 6  # ,
    LEFT_BRACE: int = 7  # {
    RIGHT_BRACE: int = 8  # }
    ASSEMBLY_DIRECTIVE: int = 9  # DAT
    INVALID: int = 10  # \0

    # Map the underlying integer associated with a particular token type to its human-friendly text equivalent
    # Important for parser class when generating error messages
    INTEGER_TO_TOKEN: dict[int, str] = {  
        END: "End Of Statement",
        INSTRUCTION: "Instruction",
        ADDRESSING_MODE: "Addressing Mode",
        VALUE: "Value",
        REGISTER: "Register",
        LABEL: "Label",
        SEPERATOR: "Instruction Seperator",
        RIGHT_BRACE: "Right Curly Brace",
        LEFT_BRACE: "Left Curly Brace",
        ASSEMBLY_DIRECTIVE: "Assembly Directive",
        INVALID: "Invalid Token"
    }

    # --Class Members / Object Attributes
    tokenType: int
    # --Inherited Class Members / Object Attributes
    tokenValue: str
    row: int
    column: int

    # --Object Methods
    def __init__(self: "TypedToken", tokenType: int, tokenValue: str, row: int, column: int) -> None:
        """Constructor for a `TypedToken` object"""

        # Call super class' constructor to initialise inherited attributes
        UntypedToken.__init__(self, tokenValue, row, column)

        # The token type, determining the the type of tokenValue being stored and how the tokenValue should be manipulated
        self.tokenType: int = tokenType  
