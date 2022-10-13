"""
Module containing the 'Preprocessor' class that inherits from the 'ArgumentProcessor' class
"""

import sys
from argumentprocessor import ArgumentProcessor
from keywords import KeyWords
from position import Position
from colour import Colour

class Preprocessor(ArgumentProcessor):
    """
    -Class encapsulating all functionality required to extract preprocessor directives from a source code file, 
        leaving actual chadsembly source code untouched
    -The extracted preprocessor directives will then be tokenised, parsed, validated and then used to 
        update the System Configuration Table using functionality inherited from the ArgumentProcessor class
    -A preprocessor directive is a command-line argument located within the source code file
    """

    # --Class Members / Object Attributes
    sourceCode: str
    commentPrefix: str
    # --Inherited members/attributes
    listOfArguments: list[str]
    directivePrefix: str
    tokenDelimiter: str
    systemConfigurationTable: dict[str, int]
    minimumValuesTable: dict[str, int]
    processingError: list[str]
    currentPositionTracker: Position

    # --Object Methods
    def __init__(self: "Preprocessor", directivePrefix: str, tokenDelimiter: str, systemConfigurationTable: dict[str, int], 
                minimumValuesTable: dict[str, int], sourceCode: str, commentPrefix: str) -> None:
        """Constructor for a `Preprocessor` object"""

        # Before the functionality inherited from the `ArgumentProcessor` class can be utilised, 
        #   we will first need to build up the list of preprocessor directives
        # We can accumulate them as we are processing the sourceCode and extracting the directives
        # The listOfArguments inherited attribute is initialised with an empty list, 
        #   ready to accumulate all extracted preprocessor directives

        # Call super class' constructor to initialise inherited attributes
        ArgumentProcessor.__init__(self, [], directivePrefix, tokenDelimiter, systemConfigurationTable, minimumValuesTable)

        self.__sourceCode: str = sourceCode  # The source code needing to be preprocessed

        # Python does not have a built-in character primitive type so a string of length 1 will be used instead
        self.__commentPrefix: str = commentPrefix[0]  # The character signifying the beginning of a comment

    def _recordError(self: "Preprocessor", errorRow: int, errorColumn: int, typeOfError: str, errorMessage: str) -> None:
        """Append a formatted error message to self._processingErrors.
        Overriding the super class' recordError to provide custom error message for the preprocessor class
        Modularising error formatting into a method creates a uniform structure for an error message keeping them consistent"""

        # Error format is: ERROR_TYPE found in line *LINE_NUMBER* at position *POSITION_IN_LINE*: *ERROR_MESSAGE*
        self._processingErrors.append(f"{typeOfError} found in line {errorRow} at position {errorColumn}: {errorMessage}")

        # The position attributes won't be updated in this method
        # If this were the case then it would assume a fixed length interval between error messages (such as 1 error per argument)
        # This wont always be the case

    def _getErrors(self: "Preprocessor") -> None:
        """Output all errors onto the terminal in a compiler-like fashion and suspend the execution of the program
        If there are not any errors then the program won't be suspended and additional computation can be done
        Modularising error output into a method will make it easier to refactor to add colour to the output
        The output will be specialised to command-line arguments and so this method should be overridden in a derived class for own custom specialised output"""

        if not self._processingErrors:  # guard clause, ensuring pre-condition that the length is greater than 0 (number of errors > 0)
            return  # return early if this pre-condition is not met

        # Output text with a red background and white foreground
        # I reset the colour then follow it with red
        # This is so all output from this point onwards (after this header) will be in red
        # This will cover all error messages and make them red
        print(f"{Colour.RED_BACKGROUND}{Colour.WHITE}Preprocessor Errors:{Colour.RESET}{Colour.RED}")

        for processingError in self._processingErrors:  # loop over each item in the list containing the errors
            print(processingError)  # output the error, colour will be added in a later prototype

        # Reset the terminal colouring so it is no longer in red
        print(Colour.RESET)

        sys.exit(-1)  # suspend program execution to ensure no additional processing can be done to avoid running into any errors

    def __skipOverComment(self: "Preprocessor", beginningIndexOfComment: int) -> int:
        """Given a beginning index, iterate until the end of the comment is reached in order to skip over it
        Rather than removing comments, we can simply skip over them to avoid the unnecessary computation of removing it"""

        # Store the source code length in a buffer variable to avoid recomputing it on each iteration in the loop
        sourceCodeLength: int = len(self.__sourceCode) 

        # Only iterate while in the indexable bounds of the source code
        while beginningIndexOfComment < sourceCodeLength and self.__sourceCode[beginningIndexOfComment] not in KeyWords.LINE_BREAK_CHARACTERS:
            # Comments span from where they begin to the end of the line so we can iterate until a newline character is found

            beginningIndexOfComment += 1  # Increment the current index to move onto the next character

        return beginningIndexOfComment  # return the new index to continue iterating from

    def __removePreprocessorDirective(self: "Preprocessor", beginningOfPreprocessorDirective: int, endingOfPreprocessorDirective: int) -> None:
        """Given an upper and lower bound, remove the substring between those bounds from the sourceCode
        Used to remove the preprocessor directive and update all other relevant information"""

        # Removing the preprocessor directive can be achieved by combining the substring from index 0 
        #   to the lower index with the upper index to the end of the string
        self.__sourceCode = self.__sourceCode[0 : beginningOfPreprocessorDirective] + \
                    self.__sourceCode[endingOfPreprocessorDirective : len(self.__sourceCode)]

    def __getPreprocessorDirective(self: "Preprocessor", lowerSubstringIndex: int) -> str:
        """Get the preprocessor directive from a given lower substring index and removes the substring from the source code"""

        # Characters signifying the end of the preprocessor directive has been reached
        # As multiple preprocessor directives can be declared on the same line, the directive prefix is included in these terminating characters
        # Comments also should be accounted for and so are also included
        # The line-break characters are what will by default connote the end of a directive
        preprocessorDirectiveTerminatingCharacters = KeyWords.LINE_BREAK_CHARACTERS + self.__commentPrefix + self._directivePrefix

        sourceCodeLength: int = len(self.__sourceCode)  # Store the source code length in a buffer variable to avoid recomputing it on each iteration in the loop 

        # Initialise with the lower substring index
        # The upper index will be incremented until one of the terminating characters are reached as to store the upper index of the substring
        upperSubstringIndex: int = lowerSubstringIndex + 1  # Begin from the position after the lowerSubstring index to begin from the character after the directive prefix

        while upperSubstringIndex < sourceCodeLength and self.__sourceCode[upperSubstringIndex] not in preprocessorDirectiveTerminatingCharacters:
            # Only iterate while in the indexable bounds of the substring and 

            upperSubstringIndex += 1  # Increment the index to move onto the next character

        preprocessorDirectiveSubstring: str = self.__sourceCode[lowerSubstringIndex : upperSubstringIndex]  # Grab the preprocessor directive from the given upper and lower bounds

        self.__removePreprocessorDirective(lowerSubstringIndex, upperSubstringIndex)  # Remove the preprocessor directive from the source code

        return preprocessorDirectiveSubstring  # Return the grabbed substring to the caller

    def __extractPreprocessorDirectives(self: "Preprocessor") -> list[Position]:
        """Get and remove all preprocessor directives from the source code, leaving actual chadsembly code untouched"""

        # As the preprocessor directives are located inside a text file, 
        #   we will need to keep track of the positions in the text files in order to provide specialised error messages that include the line and position
        # The preprocessor directives will be grabbed as substrings and so the position of the substring will need to be kept track of 
        #   so when the substrings are later tokenised we have a beginning position and row to build off of
        # As substrings are being grabbed rather than tokens being generated we cannot simply pre-generate a token with the current position in the file
        # In order to keep track of the positions for each substring, and as the substrings will be stored in the inherited self.listOfArguments attribute
        # I will use what I call a "parallel array" where each element stores the positional related data for the matching index
        # In other words: Index 0 in the parallel array will store the positional related data of the substring held in index 0 of the listOfArguments array
        # These positions can then be used as a base point when generating tokens from the substrings 
        #   in order to provide specialised error messages that include a line number as well as position in the text file
        listOfParallelPositions: list[Position] = []

        currentIndex: int = 0  # Store the current index within the source code text file (which will be processed as a string)

        while currentIndex < len(self.__sourceCode):  
            # As the length of the source code can change depending on what happens in the loop, 
            #   the length of the source code will need to be recalculated on each iteration
            # Caching the length in a static variable won't account for the volatile source code length and so errors may occur

            match self.__sourceCode[currentIndex]:  # Switch statement using the current character as the match target

                case self.__commentPrefix:  # In the case where a comment is found

                    # Skip over the comment, reassigning the current index to the new index to continue iterating from
                    currentIndex = self.__skipOverComment(currentIndex)  

                case self._directivePrefix:  # In the case where the beginning of a preprocessor directive is encountered

                    # Append a new position object, storing the line number and position of the preprocessor directive
                    listOfParallelPositions.append(Position(self._currentPositionTracker.row, self._currentPositionTracker.column))

                    # Grab the preprocessor directive, also removing it from the source code
                    self._listOfArguments.append(self.__getPreprocessorDirective(currentIndex))  

            if currentIndex < len(self.__sourceCode):  # Ensure the position is only while still in the indexable bounds of the source code string

                # Advance onto the next position resetting column to 1 if need be
                self._currentPositionTracker.advancePosition(self.__sourceCode[currentIndex], 1) 

            currentIndex += 1  # Increment the current index to move onto the next character in the string

        # Return the list of parallel positions, ready to be used in conjunction with the built up list of arguments
        return listOfParallelPositions  

    def preprocess(self: "Preprocessor"):
        """Wrapper method, binding all other methods to extract all preprocessor directives to then tokenise, parse and process them
        Should be treated as the main method of the preprocessor class, other methods should not be called individually"""

        # Store the positions of the preprocessor directives that were extracted from the source code file
        listOfParallelPositions: list[Position] = self.__extractPreprocessorDirectives()  
        
        # Rather than using a foreach loop, a normal count-controlled loop will be used
        for index in range(len(self._listOfArguments)):
            # In order to make use of the parallel array of positions the index will be needed when looping
            # For Example: 
            # On the iteration where index = 0, the position held in index 0 of the listOfParallelPositions array will be 
            #   the position of the preprocessor directive also stored at index 0 in the listOfArguments array
            
            # As the self._tokeniseArgument method uses the self._currentPositionTracker attribute to get the row and column of tokens
            # We can manipulate this by reassigning it to store a different position 
            #   that will then be used when storing the positional related data of tokens
            # This is very important as preprocessor directives are found in a text file and not from the command line
            # This means we need to keep track of the line number and position 
            #   in the line rather than the argument number and position in the argument
            self._currentPositionTracker = listOfParallelPositions[index]  

            # Generate the token stream from the given preprocessor directive and then parse it
            self._parseTokenStream(self._tokeniseArgument(self._listOfArguments[index]))  

        self._getErrors()  # Check for any errors before allowing the program to progress

        # Return all information needed to instantiate the next class in the chadsembly pipeline: The Lexer
        return (self.__sourceCode, self.__commentPrefix)
