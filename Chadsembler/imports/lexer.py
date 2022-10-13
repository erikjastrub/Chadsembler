"""
Module containing the 'Lexer' class
"""

import sys
from defaults import Defaults
from keywords import KeyWords
from position import Position
from typedtoken import TypedToken
from colour import Colour


class Lexer:
    """
    -Class encapsulating all functionality needed to tokenise a given preprocessed source-code file into tokens 
        that can then be parsed, semantically analysed and then generated into a chadsembly program
    """

    # --Class Members / Object Attributes
    sourceCode: str
    commentPrefix: str
    lexingErrors: list[str]
    currentPositionTracker: Position

    # --Object Methods
    def __init__(self: "Lexer", sourceCode: str, commentPrefix: str) -> None:
        """Constructor for a `Lexer` object"""

        self.__sourceCode: str = sourceCode  # The source code that will get tokenised

        # Python does not have a built-in character primitive type so a string of length 1 will be used instead
        self.__commentPrefix: str = commentPrefix[0]  # The character signifying the beginning of a comment

        # Empty list that will accumulate any error messages that are raised during the argument processing
        # Errors are stored here rather than thrown as soon as they're found in order to build up 
        #   a list of errors that can be outputted at the end like a compiler does
        self.__lexingErrors: list[str] = []

        # Position object that will keep track of the current argument and what point in the argument is being processed
        # Begin from line number 1 to naturally count the lines rather than count from 0
        # Begin from position 1 in the line to naturally count the position rather than count from 0
        self.__currentPositionTracker: Position = Position(1, 1)

    def __getLexingErrors(self: "Lexer") -> None:
        """Output all errors onto the terminal in a compiler-like fashion and suspend the execution of the program
        If there are not any errors then the program won't be suspended and additional computation can be done
        Modularising error output into a method will make it easier to refactor to add colour to the output"""

        if not self.__lexingErrors:  # method-guard, ensuring pre-condition that the length is greater than 0 (number of errors > 0) is met
            return  # Return early if this pre-condition is not met

        # Output text with a red background and white foreground
        # I reset the colour then follow it with red
        # This is so all output from this point onwards (after this header) will be in red
        # This will cover all error messages and make them red
        print(f"{Colour.RED_BACKGROUND}{Colour.WHITE}Lexing Errors:{Colour.RESET}{Colour.RED}")

        for lexingError in self.__lexingErrors:  # Loop over each item in the list containing the errors
            print(lexingError)  # Output the error, colour will be added in a later prototype

        # Reset the terminal colouring so it is no longer in red
        print(Colour.RESET)

        sys.exit(-1)  # Suspend program execution to ensure no additional processing can be done to avoid running into any errors

    def __recordLexingError(self: "Lexer", errorRow: int, errorColumn: int, typeOfError: str, errorMessage: str) -> None:
        """Append a formatted error message to self.__lexingErrors
		Error messages will be specialised to arguments so this method should be overridden in a derived class to allow for own custom specialised error messages
		Modularising error formatting into a method creates a uniform structure for an error message keeping them consistent"""

        # Error format is: ERROR_TYPE found in line *LINE_NUMBER* at position *POSITION_IN_LINE*: *ERROR_MESSAGE*
        self.__lexingErrors.append(f"{typeOfError} found in line {errorRow} at position {errorColumn}: {errorMessage}")

        # The position attributes won't be updated in this method.
        # If this were the case then it would assume a fixed length interval between error messages (such as 1 error per argument)
        # This wont always be the case

    def __skipOverComment(self: "Lexer", beginningIndexOfComment: int) -> None:
        """Given a beginning index, iterate until the end of the comment is reached in order to skip over it
        Rather than removing comments, we can simply skip over them to avoid the unnecessary computation of removing it"""

        sourceCodeLength: int = len(self.__sourceCode)  # Cache the length of the source code to avoid having to recompute it on each iterations

        # Only iterate while in the indexable bounds of the source code
        while beginningIndexOfComment < sourceCodeLength and self.__sourceCode[beginningIndexOfComment] not in KeyWords.LINE_BREAK_CHARACTERS:  
            # A comment spans from where they begin to the end of the line so we can iterate until a newline character is found

            beginningIndexOfComment += 1  # Increment the current index to move onto the next character
            self.__currentPositionTracker.column += 1  #  Adjust the column as we iterate until we reach the end of the file or the new-line character

        return beginningIndexOfComment  # Return the new index the caller should continue iterating over the source code from

    def __generateEndToken(self: "Lexer", tokenSubstring: str, tokenRow: int, tokenColumn: int) -> TypedToken:
        """Generate an end token, used to connote the end of the chadsembly statement or end of the file (EOF)"""

        return TypedToken(TypedToken.END, tokenSubstring, tokenRow, tokenColumn)

    def __generateBlockScopeToken(self: "Lexer", tokenSubstring: str, tokenRow: int, tokenColumn: int) -> TypedToken:
        """Determine which block scope character it is then return the corresponding token"""

        if tokenSubstring in KeyWords.LEFT_SCOPE_CHARACTERS:  # Differentiate which scope character it is to generate the correct TypedToken for it

            return TypedToken(TypedToken.LEFT_BRACE, tokenSubstring, tokenRow, tokenColumn)

        # If the substring was not a Left Brace then we can infer it is a Right Brace - the only other possibility
        return TypedToken(TypedToken.RIGHT_BRACE, tokenSubstring, tokenRow, tokenColumn)

    def __generateInstructionSeperatorToken(self: "Lexer", tokenSubstring: str, tokenRow: int, tokenColumn: int) -> TypedToken:
        """Generate an instruction seperator token, used to connote that their are multiple operands for the given instruction"""

        return TypedToken(TypedToken.SEPERATOR, tokenSubstring, tokenRow, tokenColumn)

    def __generateAddressingModeToken(self: "Lexer", tokenSubstring: str, tokenRow: int, tokenColumn: int) -> TypedToken:
        """Generate an addressing mode token, setting the token value to the addressing mode symbol of the corresponding token"""

        # In the situation where it is an addressing mode, we will use the addressing mode symbol as the token value
        # This is to meet the prerequisite that all addressing modes are addressing mode symbols under the hood
        return TypedToken(TypedToken.ADDRESSING_MODE, KeyWords.ADDRESSING_MODES[tokenSubstring], tokenRow, tokenColumn)

    def __generateLabelToken(self: "Lexer", tokenSubstring: str, tokenRow: int, tokenColumn: int) -> TypedToken:

        # Ensure the label begins with the appropriate characters
        if tokenSubstring[0] not in KeyWords.BEGINNING_OF_LABEL_CHARACTERS:

            self.__recordLexingError(tokenRow, tokenColumn, "Invalid Label Error", f"Non-value character found `{tokenSubstring[0]}`")  

        # A copy of the token column will be used for error recording purposes
        # The token copy will be incremented throughout the iteration to keep track of the current position in the token substring
        # It is important we dont mutate the original token column to preserve the beginning position of the token
        # The beginning position of the token will be needed when generating the final typed token
        tokenColumnCopy: int = tokenColumn

        for character in tokenSubstring:  # Iterate through each character in the token substring

            if character not in KeyWords.LABEL_CHARACTERS:  # Validate the value token to ensure it only consists of integer characters

                # Record an error if a non-integer character is encountered
                self.__recordLexingError(tokenRow, tokenColumnCopy, "Invalid Label Error", f"Non-label character found `{character}`")  
            
            tokenColumnCopy += 1  # Increment to store the position of the next character in the iteration

        # Return a Label Token
        # Even if any errors were encountered, still return a Label token rather than an Invalid Token
        # This is to preserve how the token was processed
        # Any errors found will be picked up on and outputted once all tokens have been generated
        return TypedToken(TypedToken.LABEL, tokenSubstring, tokenRow, tokenColumn)
        
    def __generateValueToken(self: "Lexer", tokenSubstring: str, tokenRow: int, tokenColumn: int) -> TypedToken:
        """Attempt to generate a value token, ensuring it consists of only integer values
        Errors will be recorded when a non-integer character is found"""

        # Ensure the label begins with the appropriate characters
        if tokenSubstring[0] not in KeyWords.BEGINNING_OF_VALUE_CHARACTERS:

            self.__recordLexingError(tokenRow, tokenColumn, "Invalid Value Error", f"Non-label character found `{tokenSubstring[0]}`")  

        # A copy of the token column will be used for error recording purposes
        # The token copy will be incremented throughout the iteration to keep track of the current position in the token substring
        # It is important we dont mutate the original token column to preserve the beginning position of the token
        # The beginning position of the token will be needed when generating the final typed token
        tokenColumnCopy: int = tokenColumn

        valueTokenSign: str = '+'  # Default to a plus sign

        if tokenSubstring[0] in KeyWords.VALUE_SIGNS:  # Determine if a sign is present in the value

            valueTokenSign = tokenSubstring[0]  # The sign will obviously be held at index 0
            tokenSubstring = tokenSubstring[1:]  # Update he variable to store the rest of the string, without the sign 

        if not tokenSubstring:  # If the token substring contains no characters

            # Record an empty value error
            self.__recordLexingError(tokenRow, tokenColumnCopy, "Invalid Value Error", "Empty value found, only the sign was specified")  

        for character in tokenSubstring:  # Iterate through each character in the token substring

            if character not in KeyWords.VALUE_CHARACTERS:  # Validate the value token to ensure it only consists of integer characters

                # Record an error if a non-integer character is encountered
                self.__recordLexingError(tokenRow, tokenColumnCopy, "Invalid Value Error", f"Non-value character found `{character}`")
            
            tokenColumnCopy += 1  # Increment to store the position of the next character in the iteration

        # Return a Value Token
        # Even if any errors were encountered, still return a Value token rather than an Invalid Token
        # This is to preserve how the token was processed
        # Any errors found will be picked up on and outputted once all tokens have been generated
        return TypedToken(TypedToken.VALUE, valueTokenSign + tokenSubstring, tokenRow, tokenColumn)

    def __determineTypeOfRegisterKeyword(self: "Lexer", tokenSubstring: str) -> str:
        """The 'register' keyword can either mean the general purpose register or the addressing mode
        Is it critical we are able to distinguish between the 2 as it will affect the parser and may result in various bugs"""

        # Store the upper substring index
        upperSubstringIndex = len(tokenSubstring)

        # Initialise the lower substring index with the upper substring index - 1 to begin off in the indexable bounds of the string
        lowerSubstringIndex = upperSubstringIndex - 1

        while tokenSubstring[lowerSubstringIndex] in "1234567890":  # Only iterate while integer-characters are present
            lowerSubstringIndex -= 1  # Decrement the index

        # As the loop will over-decrement the lower substring index we will need to make up for this by incrementing it at the end
        lowerSubstringIndex += 1

        keywordSubstring = tokenSubstring[0: lowerSubstringIndex]  # Grab the keyword part of the label

        # Grab the integer suffix (the integer characters at the end), if there are none it will grab an empty string
        integerSuffixSubstring = tokenSubstring[lowerSubstringIndex: upperSubstringIndex]

        # If the keyword is a general purpose register and there is an integer suffix
        if keywordSubstring in KeyWords.GENERAL_PURPOSE_REGISTER and integerSuffixSubstring:  

            return integerSuffixSubstring  # Return the integer suffix (connoting it is a general purpose register)

        # If not then we can determine it is not a general purpose register and we can return an empty string to indicate so
        return ""

    def __determineTokenType(self: "Lexer", tokenSubstring: str) -> int:
        """Given a substring, determine what token type it belongs to"""

        if tokenSubstring in KeyWords.INSTRUCTION_SET:

            return TypedToken.INSTRUCTION

        if tokenSubstring in KeyWords.SPECIAL_PURPOSE_REGISTERS:

            return TypedToken.REGISTER

        if tokenSubstring in KeyWords.ADDRESSING_MODES:

            return TypedToken.ADDRESSING_MODE

        if tokenSubstring in KeyWords.ASSEMBLY_DIRECTIVES:

            return TypedToken.ASSEMBLY_DIRECTIVE

        # Default to a label token type if none of the above special cases were matched
        return TypedToken.LABEL

    def __getTokenSubstring(self: "Lexer", lowerSubstringIndex: int) -> str:
        """Grabs the substring of the token from the source code file, will not remove the token from the source code only will grab it"""

        # All characters that will determine the end of the token substring has been reached
        tokenTerminatingCharacters: str = KeyWords.WHITE_SPACE_CHARACTERS + KeyWords.LINE_BREAK_CHARACTERS + KeyWords.OPERAND_SEPERATOR_CHARACTERS + \
            KeyWords.BLOCK_SCOPE_CHARACTERS + KeyWords.ADDRESSING_MODE_CHARACTERS + self.__commentPrefix

        upperSubstringIndex: int = lowerSubstringIndex  # Initialise the upper index pointer to begin with at the lower index pointer
        sourceCodeLength: int = len(self.__sourceCode)  # Cache the source code length to avoid recomputing it on each iteration

        while upperSubstringIndex < sourceCodeLength and self.__sourceCode[upperSubstringIndex] not in tokenTerminatingCharacters:
            # Iterate while in the indexable bounds of the array and the no substring terminating character has been reached

            upperSubstringIndex += 1  # Readjust the upper index pointer

        # Return the substring in its default cased for
        # This is to ensure tokens are all processed in their default cased form
        # This is to ensure the case-insensitivity of the chadsembler
        return Defaults.convertToCasing(self.__sourceCode[lowerSubstringIndex : upperSubstringIndex])  

    def __processTokenSubstring(self: "Lexer", tokenSubstring: str, tokenStream: list[TypedToken], tokenRow, tokenColumn) -> None:
        """Given a substring, process it to correctly determine which token type it is and append the corresponding token type to the token stream"""

        # If a value token is encountered then obviously attempt to generate a value token
        if tokenSubstring[0] in KeyWords.BEGINNING_OF_VALUE_CHARACTERS:  

            tokenStream.append(self.__generateValueToken(tokenSubstring, self.__currentPositionTracker.row, self.__currentPositionTracker.column))

        else:

            # The "REGISTER" keyword can either mean the addressing mode or the general purpose register
            # It is critical this special case is accounted for
            # The function will return an empty string if it is not a general-purpose register 
            #   and the register number if it is a general purpose register
            # An empty string equates to the boolean value of False
            # Determine which REGISTER keyword it is, if it is even a REGISTER keyword at all
            isGeneralPurposeRegister: str = self.__determineTypeOfRegisterKeyword(tokenSubstring)

            if isGeneralPurposeRegister:

                # As the "isGeneralPurposeRegister" variable will store the register number, 
                # we can use it as the token value for the typed token object we are instantiating and returning
                tokenStream.append(TypedToken(TypedToken.REGISTER, isGeneralPurposeRegister, tokenRow, tokenColumn))

            else:

                typeOfToken: int = self.__determineTokenType(tokenSubstring)  # Determine what type of token the substring is

                match typeOfToken:  # Switch statement using the typeOfToken as the match target

                    case TypedToken.ADDRESSING_MODE:
                        # In the special case where it is an addressing mode
                        # The tokenValue will need to be the symbol form of the addressing mode

                        tokenStream.append(TypedToken(typeOfToken, KeyWords.ADDRESSING_MODES[tokenSubstring], tokenRow, tokenColumn))

                    case TypedToken.LABEL:
                        tokenStream.append(self.__generateLabelToken(tokenSubstring, tokenRow, tokenColumn))

                    case _:
                        # In all other cases the typeOfToken can just be used to initialise a new TypedToken object with the substring
                        tokenStream.append(TypedToken(typeOfToken, tokenSubstring, tokenRow, tokenColumn))

    def __tokeniseSourceCode(self: "Lexer") -> list[TypedToken]:
        """Given the source code, a stream of tokens will be generated and returned
        Each token will contain contextual data about its origins
        This is critical as it allows the token stream to be parsed and semantically analysed so it may be translated into chadsembly machine code"""

        currentIndex: int = 0  # Initialise with 0 to begin iteration over the source code file from the beginning
        generatedStreamOfTokens: list[TypedToken] = []  # The token stream that will be accumulated with TypedToken objects as the source code is iterated over
        sourceCodeLength: int = len(self.__sourceCode)  # Cache the length of the source code into a variable to avoid having to recompute it on each iteration

        while currentIndex < sourceCodeLength:  # Iterate while in the indexable bounds of the source code (manipulated as a string)

            # Grab the character and store it in a buffer variable to make it easier to perform comparisons on
            # Also caches the current character as to avoid having to recompute it from the index every time it needs to be accessed in a comparison
            currentCharacter: str = self.__sourceCode[currentIndex]

            if currentCharacter == self.__commentPrefix:  # If a comment is encountered

                currentIndex = self.__skipOverComment(currentIndex)  # Skip over the comment, effectively removing it

            elif currentCharacter in KeyWords.WHITE_SPACE_CHARACTERS:  # If a non-lexer triggering whitespace character is encountered

                currentIndex += 1  # Increment the current index to skip over it as no lexing can be done on whitespace
                self.__currentPositionTracker.column += 1  # Adjust the column to compensate for the whitespace

            elif currentCharacter in KeyWords.LINE_BREAK_CHARACTERS:  # If a new-line character is encountered

                if generatedStreamOfTokens and generatedStreamOfTokens[-1].tokenType != TypedToken.END:

                    # Only append an END token (used to connote the end of a statement and line) 
                    #   if the last token in the token stream is not an END token and there are tokens present in the token stream
                    # This is done to ensure no duplicate END tokens are appended to the token stream - waste of memory 
                    generatedStreamOfTokens.append(self.__generateEndToken(Defaults.LINE_BREAK_SYMBOL, self.__currentPositionTracker.row, self.__currentPositionTracker.column))

                currentIndex += 1  # Increment the currentIndex to move off of the new-line character and onto the next character in the source code
                self.__currentPositionTracker.row += 1  # Increment the line count
                self.__currentPositionTracker.column = 1  # Reset the column attribute to begin counting from the beginning of the line again

            elif currentCharacter in KeyWords.BLOCK_SCOPE_CHARACTERS:  # If a block scope character is encountered (procedure scope characters)

                # Append a block scope token to the token stream
                generatedStreamOfTokens.append(self.__generateBlockScopeToken(currentCharacter, self.__currentPositionTracker.row, self.__currentPositionTracker.column))  
                currentIndex += 1  # Increment the currentIndex to move off of the block scope character and onto the next character in the source code
                self.__currentPositionTracker.column += 1  # Increment the column to store the position of the next character

            elif currentCharacter in KeyWords.OPERAND_SEPERATOR_CHARACTERS:  # If an instruction seperator character is encountered

                generatedStreamOfTokens.append(self.__generateInstructionSeperatorToken(Defaults.INSTRUCTION_SEPERATOR_SYMBOL, 
                                                self.__currentPositionTracker.row, self.__currentPositionTracker.column))  # Append an instruction seperator token to the token stream
                currentIndex += 1  # Increment the currentIndex to move off of the block scope character and onto the next character in the source code
                self.__currentPositionTracker.column += 1  # Increment the column to store the position of the next character

            elif currentCharacter in KeyWords.ADDRESSING_MODE_CHARACTERS:  # If an addressing mode character is encountered

                # Append an addressing mode token to the token stream
                generatedStreamOfTokens.append(self.__generateAddressingModeToken(currentCharacter, self.__currentPositionTracker.row, self.__currentPositionTracker.column))  
                currentIndex += 1  # Increment the currentIndex to move off of the addressing mode character and onto the next character in the source code
                self.__currentPositionTracker.column += 1  # Increment the column to store the position of the next character

            else: 
                # If none of the special single-character token cases were met, then we'll have to operate on a substring instead

                tokenSubstring: str = self.__getTokenSubstring(currentIndex)  # Grab the substring
                tokenSubstringLength: int = len(tokenSubstring)  # Cache the length of the substring to avoid having to recompute it

                # Process the substring to determine what type of token it is
                # It then may be appended to the stream of tokens
                self.__processTokenSubstring(tokenSubstring, generatedStreamOfTokens, self.__currentPositionTracker.row, self.__currentPositionTracker.column)

                currentIndex += tokenSubstringLength  # Readjust the currentIndex by adding the length of the substring to continue iteration from after the substring
                self.__currentPositionTracker.column += tokenSubstringLength  # Readjust the column by adding the length of the substring to store the position after the substring

        if len(self.__sourceCode) and generatedStreamOfTokens[-1].tokenType != TypedToken.END:

            # Only append an END token (used to connote the end of a statement and line) if the last token in the token stream is not an END token
            # This is done to ensure no duplicate END tokens are appended to the token stream - waste of memory 
            generatedStreamOfTokens.append(self.__generateEndToken('/', self.__currentPositionTracker.row, self.__currentPositionTracker.column))

        return generatedStreamOfTokens  # Return the stream of contextual tokens, ready to be used by the parser and semantic analyser

    def lex(self: "Lexer") -> tuple:
        """The main method of the Lexer class, combining all other methods needed to lex the source code and generate the token stream"""

        # A precondition of this method is that the source code file has a length > 0 
        # It actually contains text that can be tokenised
        # This precondition is a length check
        if self.__sourceCode:  # Same as if len(self.__sourceCode > 0)

            tokenStream: list[TypedToken] = self.__tokeniseSourceCode()  # Generate the token stream
            self.__getLexingErrors()  # Check for any errors before allowing the program to progress

            # Return all information needed to instantiate the next class in the chadsembly pipeline: The Parser
            return (tokenStream,)

        # If this point of the method is reached then it means the precondition wasn't met
        # The source code contains no text and so no tokens could have been generated
        # I will return an empty list for the token stream to signify no tokens were generated
        return ([],)
