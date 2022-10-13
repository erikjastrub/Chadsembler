"""
Module containing the 'Defaults' class
"""

class Defaults:
    """
    -Class used to group all default behaviour related functionality and variables into a single namespace
    -System defaults can be changed once here and will take affect over the whole system
    -Improves code maintainability, the whole system wont need to be refactored to reflect changes in a system default
    """

    class NULL: pass  # used to replicate NULL in languages like C/C++ and Java

    @staticmethod
    def convertToCasing(uncasedString: str) -> str:
        """Will return the string in the default letter casing"""

        # Case-insensitivity can be achieved by processing tokens in either all upper or lower case
        # Regardless which was chosen, it must be consistently used throughout all stages of assembly
        # We can define which casing should be used in here rather than throughout the whole program
        # Defining it here makes the chadsembler more modular
        # Default casing only needs to be changed once here and is reflected throughout the whole system
        # Obviously more beneficial than having to refactor all the code where default casing must be used

        return uncasedString.upper()  # Currently, a default-casing of upper-case will be used

    DIRECTIVE_PREFIX: str = '!'  # The character that'll be used to connote the beginning of a preprocessor directive
    COMMENT_PREFIX: str = ';'  # The character connoting the beginning of a comment in the source code
    TOKEN_DELIMITER: str = '='  # The character separating the configuration option from the configuration value in a command line argument
    GLOBAL_INSTRUCTION_POOL_IDENTIFIER: str = ".MAIN"  # The identifier used to access the global instruction pool
    DEFAULT_VARIABLE_VALUE: str = "0"  # The default value a variable should be initialised to

    LINE_BREAK_SYMBOL: str = '/'  # The symbol that should be used as the token value for an END token
    INSTRUCTION_SEPERATOR_SYMBOL: str = ','  # The symbol that should be used as the token value for a SEPARATOR token

    # The key that should be used to access the number of memory addresses configuration value 
    # in the configuration table
    MEMORY_CONFIGURATION_OPTION: str = "MEMORY"

    # The key that should be used to access the number of general purpose registers 
    # configuration value in the configuration table
    REGISTERS_CONFIGURATION_OPTION: str = "REGISTERS"

    # The key that should be used to access the clock speed configuration value 
    # in the configuration table
    CLOCK_CONFIGURATION_OPTION: str = "CLOCK"
