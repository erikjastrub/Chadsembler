"""
Module containing the 'Parser' class
"""

import sys
from defaults import Defaults
from symboltable import SymbolTable
from typedtoken import TypedToken
from instructionpool import InstructionPool
from symboltableentry import SymbolTableEntry
from colour import Colour

class Parser:
    """
    -Class encapsulating all functionality required to parse a token stream as well as manipulate the token stream, ensuring it is ready to be semantically analysed
    """

    # --Class Members / Object Attributes
    streamOfTokens: list[TypedToken]
    parsingErrors: list[str]
    previousBlockScopeToken: TypedToken | Defaults.NULL
    instructionPools: dict[str, InstructionPool]

    # --Object Methods
    def __init__(self: "Parser", streamOfTokens: list[TypedToken]) -> None:
        """Constructor for a `Parser` object"""

        # The list of tokens generated from the lexical analysis
        self.__streamOfTokens: list[TypedToken] = streamOfTokens

        # Empty list that will accumulate any error messages that are raised during the argument processing
        # Errors are stored here rather than thrown as soon as they're found 
        #   in order to build up a list of errors that can be outputted at the end like a compiler does
        self.__parsingErrors: list[str] = []

        # Store the previous block scope token (either a LEFT_BRACE, RIGHT_BRACE or NULL)
        # Rather than passing as an argument between  method calls, it has been made into an attribute so it can be shared between all object methods
        self.__previousBlockScopeToken: TypedToken | Defaults.NULL = Defaults.NULL

        # The token stream split into its individual instruction pools (one pool for each procedure)
        # Instructions found in the global instruction pool (outside any procedures) will be stored under the ".main" key
        # In order to not interfere with any possible user labels, the global instruction pool is stored under the ".main" entry
        # This is a special case label using a "." which cannot be used in user defined labels
        # This is to ensure there is no accidental overlap with a user label and the under the hood global instruction pool label
        self.__instructionPools: dict[str, InstructionPool] = {}
        self.__globalInstructionPool: InstructionPool = InstructionPool(Defaults.GLOBAL_INSTRUCTION_POOL_IDENTIFIER, [], SymbolTable())

    def __getParsingErrors(self: "Parser") -> None:
        """Output all errors onto the terminal in a compiler-like fashion and suspend the execution of the program
        If there are not any errors then the program won't be suspended and additional computation can be done
        Modularising error output into a method will make it easier to refactor to add colour to the output"""

        if not self.__parsingErrors:  # guard clause, ensuring pre-condition that the length is greater than 0 (number of errors > 0)
            return  # return early if this pre-condition is not met

        # Output text with a red background and white foreground
        # I reset the colour then follow it with red
        # This is so all output from this point onwards (after this header) will be in red
        # This will cover all error messages and make them red
        print(f"{Colour.RED_BACKGROUND}{Colour.WHITE}Parsing Errors:{Colour.RESET}{Colour.RED}")

        for parsingError in self.__parsingErrors:  # loop over each item in the list containing the errors
            print(parsingError)  # output the error, colour will be added in a later prototype

        # Reset the terminal colouring so it is no longer in red
        print(Colour.RESET)

        sys.exit(-1)  # suspend program execution to ensure no additional processing can be done to avoid running into any errors


    def __generateParsingErrorMessageFromContext(self: "Parser", firstToken: TypedToken, secondToken: TypedToken) -> str:
        """Given 2 tokens, a specialised error message for the given tokens will be generated
        It will be assumed the token's come after each other sequentially"""

        if firstToken.tokenType == TypedToken.END:  # Special case where the first token is an END token, connoting the statement began off incorrectly
            return f"Statement cannot begin with {TypedToken.INTEGER_TO_TOKEN[secondToken.tokenType]}"

        # Default error message
        return f"{TypedToken.INTEGER_TO_TOKEN[secondToken.tokenType]} - `{secondToken.tokenValue}` was found after {TypedToken.INTEGER_TO_TOKEN[firstToken.tokenType]} - `{firstToken.tokenValue}`"

    def __recordParsingError(self: "Parser", firstToken: TypedToken, secondToken: TypedToken) -> None:
        """Append a formatted error message to self.__parsingErrors
		Modularising error formatting into a method creates a uniform structure for an error message keeping them consistent"""

        self.__parsingErrors.append(
            f"Invalid Syntax Error: Unexpected token found in line {secondToken.row} at position {secondToken.column}: {self.__generateParsingErrorMessageFromContext(firstToken, secondToken)}")

    def __generateNextValidToken(self: "Parser", currentToken: TypedToken) -> tuple[TypedToken]:
        """Generate the next possible valid token(s) that should be found after the given token"""

        match currentToken.tokenType:

            case TypedToken.END:

                return (TypedToken.END, TypedToken.INSTRUCTION, TypedToken.LABEL, TypedToken.RIGHT_BRACE, TypedToken.LEFT_BRACE)

            case TypedToken.INSTRUCTION:

                return (TypedToken.END, TypedToken.ADDRESSING_MODE, TypedToken.VALUE, TypedToken.REGISTER, TypedToken.LABEL, TypedToken.RIGHT_BRACE)

            case TypedToken.ADDRESSING_MODE:

                return (TypedToken.VALUE, TypedToken.REGISTER, TypedToken.LABEL)

            case TypedToken.VALUE | TypedToken.REGISTER:

                return (TypedToken.END, TypedToken.SEPERATOR, TypedToken.RIGHT_BRACE, TypedToken.LEFT_BRACE)

            case TypedToken.LABEL:

                return (TypedToken.END, TypedToken.SEPERATOR, TypedToken.INSTRUCTION, TypedToken.RIGHT_BRACE, TypedToken.LEFT_BRACE, TypedToken.ASSEMBLY_DIRECTIVE)

            case TypedToken.SEPERATOR:

                return (TypedToken.ADDRESSING_MODE, TypedToken.VALUE, TypedToken.REGISTER, TypedToken.LABEL)

            case TypedToken.RIGHT_BRACE | TypedToken.LEFT_BRACE:

                return (TypedToken.END,)

            case TypedToken.ASSEMBLY_DIRECTIVE:

                return (TypedToken.END, TypedToken.VALUE)

    def __validateBlockScopeToken(self: "Parser", currentIndex: int) -> None:
        """Given a token, will validate the integrity of the token if it is a block scope token
        If a non-block scope token is passed in the method will return early"""
        
        # Store the current token in a buffer variable to avoid recomputing the current token from the given index between selection statements
        currentToken: TypedToken = self.__streamOfTokens[currentIndex]

        if currentToken.tokenType != TypedToken.LEFT_BRACE and currentToken.tokenType != TypedToken.RIGHT_BRACE:

            # A precondition for the method is that a block scope token is passed in
            # This method-guard will ensure this is the case
            return

        if currentToken.tokenType == TypedToken.LEFT_BRACE:
                
            if self.__previousBlockScopeToken is Defaults.NULL:
                # A previous block scope token of NULL connotes there is no current open block scope
                # This means they are attempting to open a new block scope while there is no current open block scope which is valid syntax
                # No error will be recorded, only the previous block scope token will be updated
                self.__previousBlockScopeToken = currentToken      

            else:
                # If the previous block scope token is opening a block scope (not NULL)
                # Then we can infer the previous block scope hasn't been closed and a new block scope is trying to be opened
                # This is not valid syntax and a custom error will be recorded
                # Chadsembly does not support nested procedures

                # A unique error for the block scoping will need to be generated and so we won't use the record parsing error which requires 2 tokens passed in as arguments
                self.__parsingErrors.append(
                    f"Invalid Syntax Error found in line {currentToken.row} at position {currentToken.column}: Cannot open new block scope until previous one was closed")

        elif currentToken.tokenType == TypedToken.RIGHT_BRACE:

            if self.__previousBlockScopeToken is Defaults.NULL:
                # If the previous block scope token is NULL then we can infer an attempt to close an unopened block scope is being made
                # This is not valid syntax as you cannot logically close something you didn't open
                # In this case a procedure scoping is trying to be closed when one was never opened

                # A unique error for the block scoping will need to be generated and so we won't use the record parsing error which requires 2 tokens passed in as arguments
                self.__parsingErrors.append(
                    f"Invalid Syntax Error found in line {currentToken.row} at position {currentToken.column}: Attempting to close a block scope when no block scope was opened to begin with")

            else:
                # If the previous block token is not NULL then that means there is an open block scope
                # This means an attempt to close an opened block scoping is being made which is valid syntax
                # No error will be recorded, only the previous block scope token will be updated to NULL
                # NULL will connote there is no active block scope
                self.__previousBlockScopeToken = Defaults.NULL

    def __preparse(self: "Parser") -> None:
        """Will match a given token sequence to the language syntax, ensuring tokens are found in the correct order, effectively parsing the token stream
        Pre-parsing will allow for additional computation such as splitting the tokens into individual instruction pools to occur"""

        currentIndex: int = 0  # Begin at index 0
        previousToken: TypedToken = TypedToken(TypedToken.END, '/', -1, -1)  # Initialise with an END token, an end token will connote the beginning of a statement
        numberOfTokens = len(self.__streamOfTokens)  # Cache the number of tokens to avoid having to recompute it on each iteration

        # Store the current token at the currentIndex if able to, otherwise assign to NULL to connote no token could be grabbed at current index

        while currentIndex < numberOfTokens:  # Iterate within the indexable bounds of the token stream

            currentToken: TypedToken =  self.__streamOfTokens[currentIndex]  # Store the current token at the current index in a buffer variable

            nextValidTokens: list[int] = self.__generateNextValidToken(previousToken)  # Generate the expected tokens that should be found after a given token

            # Treat the current token as if it is a block scope token and attempt to validate it
            # The method will return early if the current token (at the given index) is not a block scope token
            # As chadsembly allows for procedures, additional token checks will need to be made
            # These checks will be carried out by the validateBlockScopeToken() method
            self.__validateBlockScopeToken(currentIndex)

            if currentToken.tokenType not in nextValidTokens:
                # If the current token is not found in the list of next valid tokens generated from the previous then it is invalid syntax
                # An error will be recorded accordingly
                self.__recordParsingError(previousToken, currentToken)

            currentIndex += 1  # Increment the index to move onto the next token
            previousToken = currentToken  # Update the previous token to store the current token
            
        if self.__previousBlockScopeToken is not Defaults.NULL:
            # If the previous block scope token is not NULL then a block scope was never closed
            # This is invalid syntax and an error will be thrown
            self.__parsingErrors.append(
                f"Invalid Syntax Error found in line {self.__previousBlockScopeToken.row} at position {self.__previousBlockScopeToken.column}: Block scope was opened but never closed")

    def __getProcedureTokens(self: "Parser", beginningIndex: int, procedureLabelToken: TypedToken) -> int:
        """Given the starting point of a procedure, all tokens found within the block scope of the procedure will be accumulated into its own instruction pool
        In the case where the procedure already has been defined, the procedure will overwrite the old procedures instruction pool, effectively redefining and updating it"""

        currentToken: TypedToken = self.__streamOfTokens[beginningIndex]  # Store the current token in a buffer variable to make it easier to operate on
        procedureTokens: list[TypedToken] = []  # The token stream that will accumulate all tokens found within the scope of the procedure

        while currentToken.tokenType != TypedToken.RIGHT_BRACE:  # Iterate until the end of the block scope is reached (end of the procedure)

            procedureTokens.append(currentToken)  # Append the current token to the procedureTokens token stream

            beginningIndex += 1  # Increment the current index to move onto the next token
            currentToken: TypedToken = self.__streamOfTokens[beginningIndex]  # Update the currentToken variable to store the next token

        # Instantiate a new InstructionPool object and insert it into the hash map used to store all instruction pools
        self.__instructionPools[procedureLabelToken.tokenValue] = InstructionPool(procedureLabelToken.tokenValue, procedureTokens, SymbolTable())

        return beginningIndex + 1  # +1 to return index after right brace (end of the procedure)

    def __getInstructionPools(self: "Parser") -> None:
        """Once the token stream has been validated by being pre-parsed, the token stream may be split into its individual instruction pools
        There is a global instruction pool and an instruction pool for each procedure
        Each instruction pool contains its own symbol table, allowing for local scope variables"""

        currentIndex: int = 0  # Initialise with 0 to begin iteration from the beginning of the stream of tokens
        numberOfTokens: int = len(self.__streamOfTokens)  # Cache the number of tokens to avoid having to recompute it in each iteration

        while currentIndex < numberOfTokens:  # Iterate while in the indexable bounds of the token stream

            currentToken: TypedToken =  self.__streamOfTokens[currentIndex]  # Store the current token in a buffer variable to make it easier to operate on

            match currentToken.tokenType:  # Switch statement with a match target of the Token Type (an integer)

                case TypedToken.LEFT_BRACE:  # In the case where it is a Left Brace

                    # A left brace will always follow a procedure label
                    # This stray procedure label must be removed from the global instruction pool
                    # Up until this point in the program the procedure label will be one of the last tokens in the global instruction pool token stream
                    # We can access and remove it by popping the last token from the global instruction pool token stream
                    poppedToken: TypedToken = self.__globalInstructionPool.tokenStream.pop()

                    if poppedToken.tokenType == TypedToken.END:
                        # As there may optionally be a line break between the procedure label and 
                        #   left brace depending on how the user format their file, specifically how their procedures look
                        # The last token in the global instruction pool token stream may be an END token
                        # The token before this will guaranteed be the procedure label token and 
                        #   so we will simply pop off of the global instruction pool token stream once more if this is the case
                        poppedToken = self.__globalInstructionPool.tokenStream.pop()

                    # Grab all procedure tokens beginning from just after the Left Brace and End Token
                    # The poppedToken variable will have been manipulated as to store the procedure label
                    # Update the currentIndex with the new currentIndex from method call
                    currentIndex = self.__getProcedureTokens(currentIndex+2, poppedToken)

                case _:

                    # If no procedure-triggering tokens were encountered, 
                    #   then it can be inferred the current token belongs to the global instruction pool
                    # And so it is appended to the global instruction pool
                    self.__globalInstructionPool.tokenStream.append(currentToken)

            currentIndex += 1  # Increment the currentIndex to move onto the next token in the token stream

    def __parseLabel(self: "Parser", labelToken: TypedToken, instructionPool: "InstructionPool", labelContext: int) -> None:
        """Given a label, perform various label checks to ensure it is not a duplicate label or that it exists within the symbol table"""

        labelSymbol: SymbolTableEntry = instructionPool.symbolTable.get(labelToken.tokenValue)  # Get the entry for that particular symbol

        if labelSymbol is Defaults.NULL:  # If it is NULL (doesn't exist within the symbol table)

            instructionPool.symbolTable.insert(labelToken.tokenValue, -1, -1)  # Insert a new entry for that particular symbol

        else: # If it is not NULL then it does exist within the symbol table and we can perform various checks on the symbol

            match labelContext:

                case TypedToken.INSTRUCTION:

                    match labelSymbol.labelType:

                        case SymbolTable.BRANCH_LABEL:

                            self.__parsingErrors.append(
                                f"Branch Label Error found in line {labelToken.row} at position {labelToken.column}: Duplicate branch label found")

                        case SymbolTable.VARIABLE_LABEL:

                            self.__parsingErrors.append(
                                f"Branch Label Error found in line {labelToken.row} at position {labelToken.column}: Attempting to redeclare a variable label to a branch label")
                        
                        case SymbolTable.PROCEDURE_LABEL:

                            self.__parsingErrors.append("CANNOT REDECLARE PROCEDURE LABEL")

                case TypedToken.ASSEMBLY_DIRECTIVE:

                    match labelSymbol.labelType:

                        case SymbolTable.BRANCH_LABEL:

                            self.__parsingErrors.append(
                                f"Variable Label Error found in line {labelToken.row} at position {labelToken.column}: Attempting to redeclare a branch label to a variable label")

                        case SymbolTable.PROCEDURE_LABEL:

                            self.__parsingErrors.append(
                                f"Variable Label Error found in line {labelToken.row} at position {labelToken.column}: Attempting to redeclare a procedure label to a variable label")

                        # No case for a Variable Label as variable labels may be redefined

    def __removeVariable(self: "Parser", beginningIndex: int, instructionPool: "InstructionPool") -> None:
        """Given a starting index, the Assembly Directive for a variable (using the DAT keyword) will be removed from the instruction pool"""

        while instructionPool.tokenStream[beginningIndex].tokenType != TypedToken.END:  # Loop until the END of the variable declaration statement is reached

            instructionPool.tokenStream.pop(beginningIndex)  # Remove the token

    def __updateSymbolTableFromLabel(self: "Parser", currentIndex: int, instructionPool: "InstructionPool", indexedInstructionCount: int) -> None:
        """Given a label, update the symbol table accordingly"""

        # Depending on the token found after the label, we can infer very important contextual details that will help us update the symbol table accordingly
        tokenAfter: TypedToken = instructionPool.tokenStream[currentIndex+1]  # The token found after the token held at the currentIndex

        # Method-guard ensuring only Assembly Directives and Instructions are operated on
        if tokenAfter.tokenType in (TypedToken.ASSEMBLY_DIRECTIVE, TypedToken.INSTRUCTION):

            # Perform various checks on the label before getting the label from the symbol table
            self.__parseLabel(instructionPool.tokenStream[currentIndex], instructionPool, tokenAfter.tokenType)

            # Gain access to the symbol table entry for the label
            labelSymbol: SymbolTable.SymbolTableItem = instructionPool.symbolTable.get(instructionPool.tokenStream[currentIndex].tokenValue)

            match tokenAfter.tokenType:  # Switch statement with a match target of the token type (an integer)

                case TypedToken.ASSEMBLY_DIRECTIVE:  # In the case of an Assembly Directive

                    # If the token after is an Assembly Directive then we can infer the label is a variable label
                    labelSymbol.labelType = SymbolTable.VARIABLE_LABEL

                    # The label value syntactically will be held in the token found after the assembly directive
                    # This initialisation value for the variable is optional and so if it is not found then 
                    #   the default variable initialisation value will be used instead
                    labelSymbol.labelValue = int(instructionPool.tokenStream[currentIndex+2].tokenValue) \
                        if instructionPool.tokenStream[currentIndex+2].tokenType == TypedToken.VALUE else Defaults.DEFAULT_VARIABLE_VALUE

                    # Remove the variable from the instruction pool as it has been operated on and is no longer needed in the instruction pool
                    self.__removeVariable(currentIndex, instructionPool)

                case TypedToken.INSTRUCTION:  # In the case of an Instruction

                    # If the token after is an Instruction then we can infer the label is a branch label
                    labelSymbol.labelType = SymbolTable.BRANCH_LABEL

                    # The labelValue will be the current indexed instruction count which should store the memory location of the branch
                    labelSymbol.labelValue = indexedInstructionCount

    def __updateInstructionPoolSymbolTable(self: "Parser", instructionPool: "InstructionPool") -> None:
        """Will update the symbol table for a particular instruction pool"""

        # Initialise with 0 as we are index counting. Will be used to store the instruction address to jump to for branching labels
        indexedInstructionCount: int = 0

        # Initialise with 0 to begin iteration from the beginning of the instruction pool token stream
        currentIndex: int = 0

        while currentIndex < len(instructionPool.tokenStream):  
            # As the length of the token stream can change depending on what happens in the loop, 
            #   the length of the token stream will need to be recalculated on each iteration
            # Caching the length in a static variable won't account for the volatile token stream length and so errors may occurs

            # Switch statement with a match target of the token type (an integer)
            match instructionPool.tokenStream[currentIndex].tokenType:

                # If an actual label is encountered then the symbol table can be updated with that given label
                case TypedToken.LABEL:

                    self.__updateSymbolTableFromLabel(currentIndex, instructionPool, indexedInstructionCount)

                # If an END token is encountered, then the end of a statement is reached and so the indexed instruction count will be incremented
                case TypedToken.END:

                    indexedInstructionCount += 1

            currentIndex += 1  # Increment the currentIndex to move onto the next token

    def __updateSymbolTables(self: "Parser") -> None:
        """Will update the symbol tables of every instruction pool"""

        # First loop is to make sure every procedure label is inserted into the global instruction pool
        # They must all be added before updating the symbol table
        # When updating the symbol table, if not all the procedure labels are present in the global instruction pool
        # Certain errors may not get caught
        for instructionPool in self.__instructionPools:  # For each instruction pool

            # Add the procedure label to the global instruction pool (procedures are located in the global instruction pool scope)
            self.__globalInstructionPool.symbolTable.insert(instructionPool, -1, SymbolTable.PROCEDURE_LABEL)  

        # Update the global instruction pool symbol table
        self.__updateInstructionPoolSymbolTable(self.__globalInstructionPool)

        # On the second iteration we will update the symbol table fo each instructionpool
        #   now that all expected data is present
        for instructionPool in self.__instructionPools:  # For each instruction pool 

            # Update the symbol table of the current instruction pool in iteration
            self.__updateInstructionPoolSymbolTable(self.__instructionPools[instructionPool])

    def parse(self: "Parser") -> tuple:
        """The main method of the Parser class, 
            combining all other methods needed to parse the source code and split the source code into its individual instruction pools,
            readying it to be semantically analysed"""

        self.__preparse()  # Preparse the source code, performing the initial validation required upfront before any other sort of validation can occur
        self.__getParsingErrors()  # Output any pre-parsing errors that may have occurred

        self.__parsingErrors = []  # Reset the parsing errors back to an empty list so a new list of errors may be accumulated

        self.__getInstructionPools()  # Split the source code into its instruction pools
        self.__updateSymbolTables()  # Update the symbol table of each instruction pool

        self.__getParsingErrors()  # Output any errors that may have occurred while splitting the source code into instruction pools or while updating each symbol table
        
        # Return all information needed to instantiate the next class in the chadsembly pipeline: The Semantic Analyser
        return (self.__instructionPools, self.__globalInstructionPool)
