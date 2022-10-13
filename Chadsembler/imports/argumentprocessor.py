"""
Module containing the 'ArgumentProcessor' class
"""

import sys
from defaults import Defaults
from keywords import KeyWords
from position import Position
from untypedtoken import UntypedToken
from colour import Colour

class ArgumentProcessor:
    """
    -Class encapsulating all related functionality required to extract values from a list of command-line arguments
    -Will update the system configuration table accordingly, recording and raising errors at the end in a compiler-like manner
    """

    # --Class Members / Object Attributes
    listOfArguments: list[str]
    directivePrefix: str
    tokenDelimiter: str
    systemConfigurationTable: dict[str, int]
    minimumValuesTable: dict[str, int]
    processingError: list[str]
    currentPositionTracker: Position

    # --Object Methods
    def __init__(self: "ArgumentProcessor", listOfArguments: list[str], directivePrefix: str, tokenDelimiter: str,
                 systemConfigurationTable: dict[str, int], minimumValuesTable: dict[str, int]) -> None:

        self._listOfArguments: list[str] = listOfArguments  # The iterable containing the arguments to be processed

        # The character that connotes the beginning of a preprocessor directive (command line arguments found within the source code)
        # This character is optional for arguments
        # As the Preprocessor class will inherit from this class, 
        #   thinking ahead precautions that take this character into consideration will be included in this class
        # This is to ensure the inter-operability of the 2 classes as both classes are linked together in what they achieve
        # Python does not have a built-in character primitive type so a string of length 1 will be used instead
        self._directivePrefix: str = directivePrefix[0]

        # A 'delimiter' is a separator
        # In this case it is the character separating the configuration option and configuration value
        # For Example: in the argument "memory=150" the delimiter is the '=' character
        # Python does not have a built-in character primitive type so a string of length 1 will be used instead
        self._tokenDelimiter: str = tokenDelimiter[0]

        # A map storing "configuration option" : "configuration value" pairs
        # The "configuration options" are the names (stored as a string) of the run-time variables that affect how the chadsembler works
        # The "configuration values" are the integer values associated with the corresponding "configuration option"
        # A dictionary comprehension is used to ensure every key is in the default letter-casing
        # Everything is converted to the default letter-casing before being processed to keep the chadsembler case-insensitive
        self._systemConfigurationTable: dict[str, int] = systemConfigurationTable

        # A map storing "configuration option : configuration value" pairs
        # Each "configuration option" is mapped to its minimum "configuration value"
        # The minimumValuesTable and the systemConfigurationTable should both contain the same "configuration options"
        # The minimumValuesTable should not be mutated/modified and so will be treated as if it were constant
        # A dictionary comprehension is used to ensure every key is in the default letter-casing
        # Everything is converted to the default letter-casing before being processed to keep the chadsembler case-insensitive
        self._minimumValuesTable: dict[str, int] = minimumValuesTable

        # Empty list that will accumulate any error messages that are raised during the argument processing
        # Errors are stored here rather than thrown as soon as they're found in order to build up a list of errors that can be outputted at the end like a compiler does
        self._processingErrors: list[str] = []

        # Position object that will keep track of the current argument and what point in the argument is being processed
        # Begin from argument 1 to naturally count the arguments rather than count from 0
        # Begin from position 1 in the argument to naturally count the position rather than count from 0
        self._currentPositionTracker: Position = Position(1, 1)

    def _recordError(self: "ArgumentProcessor", errorRow: int, errorColumn: int, typeOfError: str, errorMessage: str) -> None:
        """Append a formatted error message to self._processingErrors.
		Error messages will be specialised to arguments so this method should be overridden 
            in a derived class to allow for own custom specialised error messages
		Modularising error formatting into a method creates a uniform structure for an error message keeping them consistent"""

        # Error format is: ERROR_TYPE found in line *LINE_NUMBER* at position *POSITION_IN_LINE*: *ERROR_MESSAGE*
        self._processingErrors.append(f"{typeOfError} found in argument {errorRow} at position {errorColumn}: {errorMessage}")

    def _getErrors(self: "ArgumentProcessor") -> None:
        """Output all errors onto the terminal in a compiler-like fashion and suspend the execution of the program
        If there are not any errors then the program won't be suspended and additional computation can be done
        Modularising error output into a method will make it easier to refactor to add colour to the output
        The output will be specialised to command-line arguments and so this method should be overridden in a derived class for own custom specialised output"""

        if not self._processingErrors:  # method-guard, ensuring pre-condition that the length is greater than 0 (number of errors > 0)

            return  # return early if this pre-condition is not met

        # Output text with a red background and white foreground
        # I reset the colour then follow it with red
        # This is so all output from this point onwards (after this header) will be in red
        # This will cover all error messages and make them red
        print(f"{Colour.RED_BACKGROUND}{Colour.WHITE}Argument Processing Errors:{Colour.RESET}{Colour.RED}")

        for processingError in self._processingErrors:    # loop over each item in the list containing the errors

            print(processingError)  # output the error, colour will be added in a later prototype

        # Reset the terminal colouring so it is no longer in red
        print(Colour.RESET)

        sys.exit(-1)  # suspend program execution to ensure no additional processing can be done to avoid running into any errors

    def _getTokens(self: "ArgumentProcessor", beginningIndex: int, currentArgument: str, substringTerminatingCharacters: str) -> list[UntypedToken]:
        """Will generate the token stream from a given argument"""

        generatedStreamOfTokens: list[UntypedToken] = []  # The token stream that will be generated from the given argument
        argumentLength: int = len(currentArgument)  # Buffer the length of the argument into a variable to avoid recomputing it on every loop

        while beginningIndex < argumentLength:  # Iterate while in the indexable bounds of the string

            # If the current character is not a substring terminating character
            if currentArgument[beginningIndex] not in substringTerminatingCharacters:
                # Then begin to generate the token

                # Store the currentIndex which will be the lower index to grab the substring from
                lowerSubstringIndex = beginningIndex
                
                # Iterate until a substring terminating character is encountered
                while beginningIndex < argumentLength and currentArgument[beginningIndex] not in substringTerminatingCharacters: 

                    beginningIndex += 1  # Increment the currentIndex to adjust the upper pointer
                    self._currentPositionTracker.column += 1  # Adjust the column accordingly

                # Instantiate an UntypedToken object, feeding it the substring as well as its row and column
                # Append this object to the stream of tokens
                generatedStreamOfTokens.append(UntypedToken(Defaults.convertToCasing(currentArgument[lowerSubstringIndex: beginningIndex]), 
                            self._currentPositionTracker.row, self._currentPositionTracker.column - (beginningIndex - lowerSubstringIndex)))

            else:
                # The only other case is that the current character is a substring terminating character
                
                beginningIndex += 1  # Increment the currentIndex to move onto the next character
                self._currentPositionTracker.column += 1  # Adjust the column accordingly

        return generatedStreamOfTokens  # Return the generated stream of tokens

    def _tokeniseArgument(self: "ArgumentProcessor", currentArgument: str) -> list[UntypedToken]:
        """Generate a stream of tokens from a given argument
        Will split on the delimiter and skip over any white-space characters, only grabbing values"""        

        if not len(currentArgument):  # Method-guard, ensuring no additional processing is done on an empty command line argument (string has a length of 0)

            return []  # Return early to avoid the unnecessary computation

        currentIndex = 0  # Initialise both variables with 0

        if currentArgument[0] == self._directivePrefix:  # If the first character in the argument is the preprocessor directive

            currentIndex = 1  # Skip over it (ignore it) by starting the iteration from index 1 (after the directive prefix)
            self._currentPositionTracker.column += 1  # Increment the column to readjust the current position

        # All characters that connote the end of the substring has been reached
        substringTerminatingCharacters: str = KeyWords.LINE_BREAK_CHARACTERS + KeyWords.WHITE_SPACE_CHARACTERS + self._tokenDelimiter

        return self._getTokens(currentIndex, currentArgument, substringTerminatingCharacters)  # Return the generated stream of tokens from the given argument

    def _isValidNumberOfTokens(self: "ArgumentProcessor", streamOfTokens: list[UntypedToken]) -> bool:
        """Perform a length-check and act accordingly, recording an error in the case of an invalid amount of tokens
        Will record specialised errors for different lengths, returning False to indicate an error was recorded
        Modularising the token stream length check will allow for parser adjustments concerning the token stream 
            to be made more effectively and modularly"""

        match len(streamOfTokens):  # Switch-case statement, matching an integer (the number of tokens)

            case 0:
                # In the case where no tokens were generated, no errors will be raised and it will be skipped
                # It should not be possible for an empty string to be passed as an argument however this should still be accounted for
                # As this class will be inherited from by the "Preprocessor" it may be possible for an empty preprocessor directive to be found
                # This should be accounted for by looking out for this special-case
                return False

            case 1:
                # In the case where only 1 token was generated means either an option or value could not be derived from the argument

                # Use the first token object's row for now
                # Syntax errors display a position of 0 to connote the whole argument
                self._recordError(streamOfTokens[0].row, streamOfTokens[0].column, "Syntax Error", "A Key : Value pair was not found")
                return False  # return early as no additional checks/validation can be done on invalid syntax

            case 2:
                # In case of valid amount of tokens, assume the first token is the option and the second is the value
                return True  # We can indicate this by returning True to indicate it is an invalid token sequence

            case _:
                # Default case will cover all cases where numberOfTokens tokens is > 2
                # Will also catch negative length (though it is not possible yet still handled by this default case block)

                # Use the first token object's row for now
                # Syntax errors display a position of 0 to connote the whole argument
                self._recordError(streamOfTokens[0].row, 0, "Syntax Error", "Should only contain a single Key : Value pair")
                return False  # return early as no additional checks/validation can be done on invalid syntax

    def _isValidConfigurationOption(self: "ArgumentProcessor", configurationOption: UntypedToken) -> bool:
        """Perform a validity check and act accordingly, recording an error in the case of an invalid configuration option
        Modularising the validity check will make it easier to add more specialised error messages 
            and target different invalid configuration options if need be"""

        # The keys in self.systemConfigurationTable are all the valid configuration options that can be updated
        if configurationOption.tokenValue not in self._systemConfigurationTable:
            # If configuration option is not in this list of keys (the options), then it is obviously an invalid configuration option

            self._recordError(configurationOption.row, configurationOption.column, "Unknown Option Error", "Option is not recognised")
            return False  # Indicate an error has been recorded and the configuration option is not valid

        # If this point is reached then no errors were found
        return True  # Return True to indicate so

    def _containsNoSign(self: "ArgumentProcessor", configurationValue: UntypedToken) -> bool:
        """Perform a presence check on the first character of the configuration value to determine if it is a sign or not
        Will record specialised errors for different lengths, returning False to indicate an error was recorded
        Modularising the sign presence check will allow parser adjustments concerning the configuration value to be made more effectively and modularly"""


        # If the user did include the sign (+ or -) it will obviously be at the start (at index 0)
        # We're only examining the first character to check if its a '+' or a '-'
        match configurationValue.tokenValue[0]:

            case '+':
                # A sign should not be specified at all
                self._recordError(configurationValue.row, configurationValue.column, "Invalid Value Error", 
                                  "Do not specify the sign of a configuration value")

            case '-':
                # A configuration value cannot be negative
                self._recordError(configurationValue.row, configurationValue.column, "Invalid Value Error", 
                                  "A configuration value must be a non-negative, denary integer")

            case _:
                # Return True indicating no sign was found and no errors were recorded
                return True

        # If no sign was found, true would have been returned and this point of the function would have never been reached
        # If this point was reached then a sign was found and an error was recorded and so False is returned
        return False

    def _isValidConfigurationValue(self: "ArgumentProcessor", unvalidatedConfigurationValueToken: UntypedToken) -> bool:
        """Perform a validity check on the configuration value to ensure it only consists of number characters (characters representing integer values)
        In other words, make sure the configuration value is an integer represented as a string
        This is done in order to meet the pre-condition that a configuration value can be converted to an integer
        Modularising this validity check means parser adjustments concerning the configuration option can be made more effectively and modularly
        For example: Other numeric systems (binary, octal and hex) may be added by refactoring this function to account for it"""

        # Store validity as boolean value and assume it is valid to begin with
        # Rather than returning when an invalid character is found, the variable will be set to false and returned at the end rather than in the loop
        # Returning inside the loop will cut out early and not character can be checked meaning some errors may not get recorded
        isValidConfigurationValue: bool = True

        # Copy integer into buffer variable to avoid mutating the object attribute
        # Mutating the object attribute rather than a copy will make the object store the wrong starting point of its position in the argument
        currentPositionCopy: int = unvalidatedConfigurationValueToken.column

        for character in unvalidatedConfigurationValueToken.tokenValue:

            # The encoding integer for '0' and '9' is 48 and 57 respectively, 
            # we can check the ordinal value of the current character is in these bounds to check if it's a number
            if not (47 < ord(character) < 58):  # More efficient way of checking if character is a number - better version of "if character not in "0123456789"

                self._recordError(unvalidatedConfigurationValueToken.row, currentPositionCopy, "Invalid Value Error", "Value must only contain integers")
                isValidConfigurationValue = False  # Update variable to indicate an error was found

            currentPositionCopy += 1  # Increment the currentPositionCopy to store next position of next character

        return isValidConfigurationValue  # Return validity of configuration value

    def _updateSystemConfigurationTable(self: "ArgumentProcessor", targetConfigurationOptionToken: UntypedToken, 
                                        targetConfigurationValueToken: UntypedToken) -> None:
        """Attempt to update the system configuration table, ensuring the configuration value is within the acceptable bounds
        An error will be recorded and the system table not updated in the situation where the configuration option is 
            not within the acceptable bounds of the corresponding configuration option
        Modularising updating the configuration table will make it easier to target how the configuration table is 
            manipulated by the parser as additional validity checks can be made if need be"""

        # Prior checks on the configuration value will ensure the integrity and validity of the configuration value
        # This will ensure the configuration value will always consist of numbers 
        #   making sure the precondition that the configuration option can be converted to an integer is met
        # It can be safely converted to an integer without any exceptions being raised as a result of this
        configurationValueAsInteger: int = int(targetConfigurationValueToken.tokenValue)

        # Store the corresponding minimum value for the configuration option
        minimumConfigurationValue: int = self._minimumValuesTable[targetConfigurationOptionToken.tokenValue]  

        if configurationValueAsInteger < minimumConfigurationValue:  # Perform a bounds check

            self._recordError(targetConfigurationValueToken.row, targetConfigurationValueToken.column, "Minimum Value Error", 
                                f"Value is below the minimum of {minimumConfigurationValue}")

        else:
            # If the above condition was not met then it is inferred that the configuration value >= minimum configuration value 
            # and so it is suitable to update the system configuration table

            # Remap the configuration option to store the new configuration value
            self._systemConfigurationTable[targetConfigurationOptionToken.tokenValue] = configurationValueAsInteger

    def _parseTokenStream(self: "ArgumentProcessor", streamOfTokens: list[UntypedToken]) -> None:
        """Given a stream of untyped tokens, the method will validate the stream of tokens and then attempt to update the system table accordingly"""

        if not self._isValidNumberOfTokens(streamOfTokens):  # Determine if there is the right amount of tokens and act accordingly depending on return value 
            return  # Return if invalid to avoid performing computation on an invalid amount of tokens (invalid syntax)

        # In case of valid amount of tokens, assume the first token is the option and the second is the value
        configurationOption, configurationValue = streamOfTokens  # Shorthand for assigning each variable to index 0 and 1 respectively

        if not self._isValidConfigurationOption(configurationOption) or \
           not self._containsNoSign(configurationValue) or \
           not self._isValidConfigurationValue(configurationValue):

           # isValidConfigurationOption() -> Determine if the assumed to be configuration option actually contains a valid configuration option
           # An invalid key means no default/minimum configuration option can be found for the target key and so the program will crash

           # containsNoSign() -> Determine if the assumed to be configuration value contains a sign or not
           # If it does then it is an invalid configuration option as a configuration option should only consist of numbers
           # No sign should be specified either, it should be inferred the value is a base 10 (denary) non-negative (only positive) integer
           
           # isValidConfigurationValue() -> Determine if the assumed to be configuration value consists only of number character
           # If it does contain non-number characters then the value cannot be converted to an integer and so it is not a valid configuration value
           
           return  # Return early to avoid processing an invalid configuration option

        # If none of the above checks were evaluated to be true and this point in the method was reached
        # It can then be inferred that both the configuration option and value are valid and so the system configuration table can be safely updated
        # All pre-conditions such as  a deary integer-only configuration value and a valid configuration option will have been met meaning
        self._updateSystemConfigurationTable(configurationOption, configurationValue)  # Update the target configuration option with the given configuration value if able to

    def argumentProcess(self: "ArgumentProcessor") -> tuple:
        """The main method of the ArgumentProcessor class, used as a wrapper method, combining all other methods to correctly process all command line arguments"""

        for argument in self._listOfArguments:  # Iterate through each argument in the list of arguments

            self._parseTokenStream(self._tokeniseArgument(argument))  # Attempt to parse, validate and update the system configuration table from the generated token stream
            self._currentPositionTracker.row += 1  # Increment row to store the position of the next argument
            self._currentPositionTracker.column = 1  # Reset column to begin position tracking from the beginning again

        self._getErrors()  # Check for any errors before allowing the program to progress

        # Return all information needed to instantiate the next class in the chadsembly pipeline: The Preprocessor
        return (self._directivePrefix, self._tokenDelimiter, self._systemConfigurationTable, self._minimumValuesTable)
