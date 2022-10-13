"""
Module containing the 'SemanticAnalyser' class
"""

import sys
from defaults import Defaults
from keywords import KeyWords
from symboltable import SymbolTable
from symboltableentry import SymbolTableEntry
from typedtoken import TypedToken
from instructionpool import InstructionPool
from operand import Operand
from colour import Colour

class SemanticAnalyser:
    """
    -Class encapsulating all data and functionality required to Semantically Analyse a stream of tokens
    -Default operands are inserted
    -Number of operands are matched to the instructions
    -Addressing mode is matched to the actual operand value
    -Special case rules and exceptions are dealt with and accounted for
    """
    
    # --Class Members / Object Attributes
    instructionPools: dict[str, InstructionPool]
    globalInstructionPool: InstructionPool
    semanticAnalyserErrors: list[str]

    # --Object Methods
    def __init__(self: "SemanticAnalyser", instructionPools: dict[str, InstructionPool], globalInstructionPool: InstructionPool) -> None:
        """Constructor for a `SemanticAnalyser` object"""

        # The stream of tokens located in the local scopes of all procedures
        self.__instructionPools: dict[str, InstructionPool] = instructionPools

        # The token stream storing all global tokens (tokens not found within the scope of a procedure)
        self.__globalInstructionPool: InstructionPool = globalInstructionPool
        
        # Empty list that will accumulate any error messages that are raised during the Semantic Analysis
        # Errors are stored here rather than thrown as soon as they're found in order to build up a list of errors that can be outputted at the end like a compiler does
        self.__semanticAnalyserErrors: list[str] = []

    def __getSemanticAnalysisErrors(self: "SemanticAnalyser") -> None:
        """Output all errors onto the terminal in a compiler-like fashion and suspend the execution of the program
        If there are not any errors then the program won't be suspended and additional computation can be done
        Modularising error output into a method will make it easier to refactor to add colour to the output"""

        if not self.__semanticAnalyserErrors:  # guard clause, ensuring pre-condition that the length is greater than 0 (number of errors > 0)
            return  # return early if this pre-condition is not met

        # Output text with a red background and white foreground
        # I reset the colour then follow it with red
        # This is so so all output from this point onwards (after this header) will be in red
        # This will cover all error messages and make them red
        print(f"{Colour.RED_BACKGROUND}{Colour.WHITE}Semantic Analysis Errors:{Colour.RESET}{Colour.RED}")

        for semanticAnalyserError in self.__semanticAnalyserErrors:  # loop over each item in the list containing the errors
            print(semanticAnalyserError)  # output the error, colour will be added in a later prototype

        # Reset the terminal colouring so it is no longer in red
        print(Colour.RESET)

        sys.exit(-1)  # suspend program execution to ensure no additional processing can be done to avoid running into any errors

    def __recordSemanticAnalysisError(self: "SemanticAnalyser", errorRow: int, errorColumn: int, typeOfError: str, errorMessage: str) -> None:
        """Append a formatted error message to self.__semanticAnalysisErrors
		Modularising error formatting into a method creates a uniform structure for an error message keeping them consistent"""

        self.__semanticAnalyserErrors.append(f"{typeOfError} found in line {errorRow} at position {errorColumn}: {errorMessage}")

    def __countNumberOfOperands(self: "SemanticAnalyser", beginningOfOperands: int, instructionPool: InstructionPool) -> int:
        """Will count the number of operands there are for a given instruction"""

        numberOfOperands: int = 0  # Initialise with 0 to begin counting up the amount of operands present

        while instructionPool.tokenStream[beginningOfOperands].tokenType != TypedToken.END:  # Iterate until the end of the statement is reached

            if instructionPool.tokenStream[beginningOfOperands].tokenType in (TypedToken.VALUE, TypedToken.REGISTER, TypedToken.LABEL):  # If an operand value is encountered
                
                numberOfOperands += 1 # Increment the number of operands

            beginningOfOperands += 1  # Increment the index counter to move onto the next token

        return numberOfOperands  # Return the amount of operands counted

    def __getOperand(self: "SemanticAnalyser", beginningOfOperand: int, instructionPool: InstructionPool) -> Operand:
        """Get the operand held at the given position, will insert default operand values and addressing modes"""

        # Store the current operand token in a variable to make it easier to operate on and reaccess it
        operandToken: TypedToken = instructionPool.tokenStream[beginningOfOperand]  

        match operandToken.tokenType:  # Switch statement with a match target of a token type (an integer)

            case TypedToken.SEPERATOR:

                return self.__getOperand(beginningOfOperand+1, instructionPool)

            # If END is encountered then no addressing mode or operand value is present and both a default addressing mode and register are inserted
            case TypedToken.END:

                 # Insert default register at current index first
                instructionPool.tokenStream.insert(beginningOfOperand, TypedToken(TypedToken.REGISTER, KeyWords.ACCUMULATOR, operandToken.row, operandToken.column))

                # Insert default addressing mode at current index so it gets placed before the register
                instructionPool.tokenStream.insert(beginningOfOperand, TypedToken(TypedToken.ADDRESSING_MODE, KeyWords.REGISTER_ADDRESSING_MODE, operandToken.row, operandToken.column))

                if instructionPool.tokenStream[beginningOfOperand-1].tokenType in (TypedToken.REGISTER, TypedToken.LABEL, TypedToken.VALUE):

                    # Insert seperator token if it is inferred to be the second operand being grabbed
                    instructionPool.tokenStream.insert(beginningOfOperand, TypedToken(TypedToken.SEPERATOR, Defaults.INSTRUCTION_SEPERATOR_SYMBOL, operandToken.row, operandToken.column))
                    return Operand(instructionPool.tokenStream[beginningOfOperand+1], instructionPool.tokenStream[beginningOfOperand+2])

            # If a Register, Label or Value is encountered then no addressing mode is present and a default addressing mode is inserted
            case TypedToken.REGISTER | TypedToken.LABEL | TypedToken.VALUE:

                # Insert default addressing mode at current index
                instructionPool.tokenStream.insert(beginningOfOperand, TypedToken(TypedToken.ADDRESSING_MODE, KeyWords.DIRECT_ADDRESSING_MODE, operandToken.row, operandToken.column))

        # Instantiate an operand object to group operand related data and return it
        return Operand(instructionPool.tokenStream[beginningOfOperand], instructionPool.tokenStream[beginningOfOperand+1])

    def __analyseProcedureOperand(self: "SemanticAnalyser", procedureOperand: "Operand", instructionPool: InstructionPool) -> None:
        """Analyse a given procedure label"""

        # Get the symbol from the symbol table
        labelSymbol: SymbolTableEntry = instructionPool.symbolTable.get(procedureOperand.operandValue.tokenValue)

        # If the procedure label was not found in the local scope
        if labelSymbol is Defaults.NULL:

                # Attempt to get the label from the global scope
                labelSymbol = self.__globalInstructionPool.symbolTable.get(procedureOperand.operandValue.tokenValue)
        
        # If the label doesn't exist, then it is an invalid procedure label
        if labelSymbol is Defaults.NULL:

            self.__recordSemanticAnalysisError(
                procedureOperand.operandValue.row, procedureOperand.operandValue.column, 
                "Invalid Procedure Call Error", "Attempting to call a non-existent procedure")

    def __analyseVariableOperand(self: "SemanticAnalyser", variableOperand: "Operand", instructionPool: InstructionPool) -> None:
        """Analyse a given variable label"""

        # Get the local symbol for the variable
        localLabelSymbol: SymbolTableEntry = instructionPool.symbolTable.get(variableOperand.operandValue.tokenValue)

        # Get the global symbol for the variable
        globalLabelSymbol: SymbolTableEntry = self.__globalInstructionPool.symbolTable.get(variableOperand.operandValue.tokenValue)

        # If the label is neither in the local scope or global scope then it is an undeclared variable
        if localLabelSymbol is Defaults.NULL and globalLabelSymbol is Defaults.NULL:

            self.__recordSemanticAnalysisError(
                variableOperand.operandValue.row, variableOperand.operandValue.column, 
                "Invalid Label Error", "Attempting to use an undeclared label as a variable")
        
        else:

            # Determine which scoping variable to use and analyse
            labelSymbol: SymbolTableEntry = globalLabelSymbol if localLabelSymbol is Defaults.NULL else localLabelSymbol

            match labelSymbol.labelType:  # Switch statement with a match target of the label type (an integer)

                case SymbolTable.BRANCH_LABEL:  # A variable label obviously cannot be a Branch label

                    self.__recordSemanticAnalysisError(
                        variableOperand.operandValue.row, variableOperand.operandValue.column, 
                        "Invalid Label Error", "Attempting to use a branch label as an instruction operand")

                case SymbolTable.PROCEDURE_LABEL:  # A variable label obviously cannot be a Procedure label

                    self.__recordSemanticAnalysisError(
                        variableOperand.operandValue.row, variableOperand.operandValue.column, 
                        "Invalid Label Error", "Attempting to use a procedure label as an instruction operand")

    def __analyseRegisterOperand(self: "SemanticAnalyser", registerOperand: "Operand") -> None:
        """Analyse a register operand, ensuring the addressing mode is semantically correct"""

        # If the token value is not a register
        if registerOperand.addressingMode.tokenValue != KeyWords.REGISTER_ADDRESSING_MODE:

            self.__recordSemanticAnalysisError(
                registerOperand.addressingMode.row, registerOperand.addressingMode.column, 
                "Invalid Addressing Mode Error", "Non-register addressing mode paired with a register")

        if registerOperand.operandValue.tokenValue == '0':  # General Purpose Register 0 cannot be accessed

            self.__recordSemanticAnalysisError(
                registerOperand.operandValue.row, registerOperand.operandValue.column, 
                "Invalid Register Error", "Cannot access general purpose register 0")


    def __analyseBranchOperand(self: "SemanticAnalyser", branchOperand: "Operand", instructionPool: InstructionPool) -> None:
        """Analyse a branch operand, ensuring only a branch label addressed in DIRECT mode is used"""

        # Check if both the addressing mode is in DIRECT mode and the operand is a label
        if branchOperand.addressingMode.tokenValue == KeyWords.DIRECT_ADDRESSING_MODE and branchOperand.operandValue.tokenType == TypedToken.LABEL:

            labelSymbol: SymbolTableEntry = instructionPool.symbolTable.get(branchOperand.operandValue.tokenValue)  # Get the symbol for the label

            if labelSymbol is Defaults.NULL:  # If it is null then an attempt to branch to an unknown location is being made

                self.__recordSemanticAnalysisError(
                    branchOperand.operandValue.row, branchOperand.operandValue.column, 
                    "Invalid Branch Error", "Attempting to branch to non-existent location")

        else:  # If the previous valid case is not met then the operand is invalid and specific error messages will be recorded

            # If the addressing mode is not in DIRECT mode

            if branchOperand.addressingMode.tokenValue != KeyWords.DIRECT_ADDRESSING_MODE:

                self.__recordSemanticAnalysisError(
                    branchOperand.operandValue.row, branchOperand.operandValue.column, 
                    "Invalid Addressing Mode Error", "Source operand in branch instruction must be addressed in DIRECT mode")

            if branchOperand.operandValue.tokenType != TypedToken.LABEL:  # If the operand is not a label

                self.__recordSemanticAnalysisError(
                    branchOperand.operandValue.row, branchOperand.operandValue.column, 
                    "Invalid Operand Error", "Source operand in branch instruction must be a branch label")

    def __analyseOutputInstruction(self: "SemanticAnalyser", outputInstructionOperand: "Operand", instructionPool: InstructionPool) -> None:
        """Analyse the special-case output instructions"""

        match outputInstructionOperand.operandValue.tokenType:  # Switch case with a match target of the token type (an integer)
        
            case TypedToken.LABEL:

                self.__analyseVariableOperand(outputInstructionOperand, instructionPool)  # Analyse the label

            case TypedToken.REGISTER:

                self.__analyseRegisterOperand(outputInstructionOperand)  # Analyse the register

    def __analyseCallInstruction(self: "SemanticAnalyser", callInstructionOperand: "Operand", instructionPool: InstructionPool) -> None:
        """Analyse the special-case procedure calling CALL instruction"""

        if callInstructionOperand.operandValue.tokenType == TypedToken.LABEL:  # If the operand is a label

            # Grab the symbol for the label
            labelSymbol: SymbolTableEntry = instructionPool.symbolTable.get(callInstructionOperand.operandValue.tokenValue)

            # If the procedure label was not found in the local scope
            if labelSymbol is Defaults.NULL:

                # Attempt to get the label from the global scope
                labelSymbol = self.__globalInstructionPool.symbolTable.get(callInstructionOperand.operandValue.tokenValue)

            if labelSymbol is Defaults.NULL:

                self.__recordSemanticAnalysisError(
                callInstructionOperand.operandValue.row, callInstructionOperand.operandValue.column, 
                "Invalid Procedure Error", "Attempting to call non-existent procedure")

            elif labelSymbol.labelType != SymbolTable.PROCEDURE_LABEL:  # If the label type is not a procedure label

                self.__recordSemanticAnalysisError(
                    callInstructionOperand.operandValue.row, callInstructionOperand.operandValue.column, 
                    "Invalid Operands Error", "Call instruction operand must be a procedure label")  # Record invalid operand error

            elif callInstructionOperand.addressingMode.tokenValue != KeyWords.DIRECT_ADDRESSING_MODE:  # Else if the addressing mode is not in direct mode

                # Record invalid addressing mode error
                self.__recordSemanticAnalysisError(
                    callInstructionOperand.addressingMode.row, callInstructionOperand.addressingMode.column, 
                    "Invalid Addressing Mode Error", "Call instruction operand must be a procedure label addressed in direct addressing mode")

            else:  # If none of the above error-cases were met, then the operand has valid semantics and so the procedure label can then be analysed

                self.__analyseProcedureOperand(callInstructionOperand, instructionPool)

        else:  # If the operand wasn't a label then it is invalid semantics and so a record is recorded

            self.__recordSemanticAnalysisError(
                callInstructionOperand.operandValue.row, callInstructionOperand.operandValue.column, 
                "Invalid Operands Error", "Call instruction operand must be a label")

    def ___analyseInputInstruction(self: "SemanticAnalyser", inputInstructionOperand: "Operand", instructionPool: InstructionPool) -> None:
        """Analyse the special-case input gathering INP instruction"""

        # If the instruction addressing mode is in immediate mode
        if inputInstructionOperand.addressingMode.tokenValue != KeyWords.REGISTER_ADDRESSING_MODE:

            # The INP instruction's operand cannot be addressed in immediate addressing mode
            # Record an invalid addressing mode error
            self.__recordSemanticAnalysisError(
                inputInstructionOperand.addressingMode.row, inputInstructionOperand.addressingMode.column, 
                "Invalid Addressing Mode Error", "Input instruction operand must be addressed in register addressing mode")  
        
        else:

            self.__analyseRegisterOperand(inputInstructionOperand)

    def __analyseAddressingMode(self: "SemanticAnalyser", instructionOperand: "Operand", instructionPool: InstructionPool) -> None:
        """Analyse the addressing mode of an operand, ensuring it is semantically correct"""

        match instructionOperand.addressingMode.tokenValue:  # Switch case with a match target of the token value (a character)

            case KeyWords.REGISTER_ADDRESSING_MODE:  # In the case where it is in register addressing mode

                if instructionOperand.operandValue.tokenType != TypedToken.REGISTER:

                    self.__recordSemanticAnalysisError(
                        instructionOperand.operandValue.row, instructionOperand.operandValue.column, 
                        "Invalid Operand Error", f"Non-register paired with register addressing mode")

    def __analyseOperand(self: "SemanticAnalyser", instructionOperand: "Operand", operandNumber: int, instructionPool: InstructionPool) -> None:
        """Will analyse a generic operand, also taking into consideration its operand number"""

        self.__analyseAddressingMode(instructionOperand, instructionPool)

        if operandNumber == 2:  # If the operand is the second operand then special second operand checks must be made

            if instructionOperand.operandValue.tokenType == TypedToken.REGISTER:  # Check if the second operand is a register

                self.__analyseRegisterOperand(instructionOperand)  # If so then analyse the register

            else:
                # if not then record an error as the second operand must be a register
                self.__recordSemanticAnalysisError(
                    instructionOperand.operandValue.row, instructionOperand.operandValue.column, 
                    "Invalid Operand Error", f"Second operand must be a register")

        else:  # In the case of any other number of operands

            match instructionOperand.operandValue.tokenType:  # Switch case with a match target of the token type (an integer)

                case TypedToken.LABEL:

                    self.__analyseVariableOperand(instructionOperand, instructionPool)  # Analyse variable label

                case TypedToken.REGISTER:

                    self.__analyseRegisterOperand(instructionOperand)  # Analyse register

    def __analyseSingleOperandInstruction(self: "SemanticAnalyser", singleOperandInstruction: TypedToken, beginningOfOperands: int, instructionPool: InstructionPool) -> None:
        """Analyse a special single-operand instruction"""
        
        if instructionPool.tokenStream[beginningOfOperands].tokenType == TypedToken.END and \
            singleOperandInstruction.tokenValue in KeyWords.EXPLICIT_SINGLE_OPERAND_INSTRUCTIONS:
            # Fancy way of checking if there are no operands are present (END of statement instead of operands were found)
            # Only applies for explicit single operand instructions (the operand must be stated)

            # If no operand is present and the instruction is an explicit operand instruction, 
            #   then an error is recorded as the operand cannot be inferred
            self.__recordSemanticAnalysisError(
                singleOperandInstruction.row, singleOperandInstruction.column, 
                "Invalid Operands Error", f"Operand must explicitly be present for a {singleOperandInstruction.tokenValue} instruction")

        else:  # Defaults case means no initial errors were encountered
            
            # Get the operand, inserting default tokens if need be
            instructionOperand: Operand = self.__getOperand(beginningOfOperands, instructionPool)
            self.__analyseAddressingMode(instructionOperand, instructionPool)

            # Switch statement with a match target of the token value (a string)
            match singleOperandInstruction.tokenValue:
                # As there are a limited amount of single-operand instructions, 
                #   we can address each one individually within this match-case statement

                case KeyWords.OUT | KeyWords.OUTC | KeyWords.OUTB:  # Output related instructions

                    self.__analyseOutputInstruction(instructionOperand, instructionPool)

                case KeyWords.CALL:  # Procedure calling related instruction

                    self.__analyseCallInstruction(instructionOperand, instructionPool)

                case KeyWords.INP:  # Input related instructions

                    self.___analyseInputInstruction(instructionOperand, instructionPool)

    def __analyseBranchInstruction(self: "SemanticAnalyser", beginningOfOperands: int, instructionPool: InstructionPool) -> None:
        """Analyse the special case instruction pointer manipulating BRANCH instructions"""

        # Grab the first operand
        sourceOperand: Operand = self.__getOperand(beginningOfOperands, instructionPool)

        # Grab the second operand at beginningOfOperands+2  beginning after the fist operand and seperator token
        destinationOperand: Operand = self.__getOperand(beginningOfOperands+2, instructionPool)

        # The source operand should contain the branch address and so special-case validation will be performed on it
        self.__analyseBranchOperand(sourceOperand, instructionPool)  

         # The second operand will get validated as normal
        self.__analyseOperand(destinationOperand, 2, instructionPool) 

    def __analyseGenericDoubleOperandInstruction(self: "SemanticAnalyser", beginningOfOperands: int, instructionPool: InstructionPool) -> None:
        """Analyse a non-special-case double operand instruction"""

        # Grab the first operand
        sourceOperand: Operand = self.__getOperand(beginningOfOperands, instructionPool)

        # Grab the second operand at beginningOfOperands+3 beginning after the fist operand and seperator token
        destinationOperand: Operand = self.__getOperand(beginningOfOperands+2, instructionPool)

        self.__analyseOperand(sourceOperand, 1, instructionPool)  # Analyse the first operand - the source operand
        self.__analyseOperand(destinationOperand, 2, instructionPool)  # Analyse the second operand - the destination operand

    def __analyseDataFlowInstruction(self: "SemanticAnalyser", beginningOfOperands: int, instructionPool: InstructionPool) -> None:
        """Analyse a special-case data transfer instruction double operand instruction"""

        # Grab the first operand
        sourceOperand: Operand = self.__getOperand(beginningOfOperands, instructionPool)

        # Grab the second operand at beginningOfOperands+3 beginning after the fist operand and seperator token
        destinationOperand: Operand = self.__getOperand(beginningOfOperands+2, instructionPool)

        if sourceOperand.addressingMode.tokenValue == KeyWords.IMMEDIATE_ADDRESSING_MODE:

            self.__recordSemanticAnalysisError(
                sourceOperand.addressingMode.row, sourceOperand.addressingMode.column, 
                "Invalid Addressing Mode Error", "Cannot address a data flow instruction in immediate mode")

        self.__analyseOperand(sourceOperand, 1, instructionPool)  # Analyse the first operand - the source operand
        self.__analyseOperand(destinationOperand, 2, instructionPool)  # Analyse the second operand - the destination operand

    def __analyseDoubleOperandInstruction(self: "SemanticAnalyser", doubleOperandInstruction: TypedToken, beginningOfOperands: int, instructionPool: InstructionPool) -> None:
        """Analyse a double operand chadsembly instruction, ensuring at least one operand is explicitly stated and the second operand is always a register"""

        # Fancy way of checking if there are no operands are present (END of statement instead of operands were found)
        if instructionPool.tokenStream[beginningOfOperands].tokenType == TypedToken.END:

            # If no operand is present and the instruction is an explicit operand instruction, then an error is recorded as the operand cannot be inferred
            self.__recordSemanticAnalysisError(
                doubleOperandInstruction.row, doubleOperandInstruction.column, 
                "Invalid Operands Error", "The SOURCE operand for any double operand instruction must be explicitly stated")

        else:  # Defaults case means no initial errors were encountered

            if doubleOperandInstruction.tokenValue in KeyWords.BRANCH_INSTRUCTIONS:

                self.__analyseBranchInstruction(beginningOfOperands, instructionPool)

            elif doubleOperandInstruction.tokenValue in KeyWords.DATA_FLOW_INSTRUCTIONS:

                self.__analyseDataFlowInstruction(beginningOfOperands, instructionPool)
            
            else:
                
                self.__analyseGenericDoubleOperandInstruction(beginningOfOperands, instructionPool)

    def __analyseInstruction(self: "SemanticAnalyser", beginningOfInstruction: int, instructionPool: InstructionPool) -> None:
        """Given the beginning of an instruction, this method will analyse the instruction and perform various instruction related checks"""

        # Grab the instruction and store it in a buffer variable to make it easier to operate on and analyse
        chadsemblyInstruction: TypedToken = instructionPool.tokenStream[beginningOfInstruction]

        # Count the number of operands present in the instruction
        # beginningOfInstruction+1 is the index (relative to the beginning of the instruction) from which the instruction operands should begin
        numberOfOperands: int = self.__countNumberOfOperands(beginningOfInstruction, instructionPool)

        # The amount of operands, at the most, that should be present for the given instruction
        maximumOperandsForInstruction: int = KeyWords.NUMBER_OF_INSTRUCTION_OPERANDS[chadsemblyInstruction.tokenValue]

        if numberOfOperands > maximumOperandsForInstruction:

            # If the numberOfOperands  exceed the max operands for the instruction then an error will be recorded
            self.__recordSemanticAnalysisError(
                chadsemblyInstruction.row, chadsemblyInstruction.column, 
                "Invalid Operands Error", f"{numberOfOperands} operands given for instruction that accepts, at most, {maximumOperandsForInstruction} operands")

        else:

            match maximumOperandsForInstruction:  # Switch statement matching the maximumOperandForInstruction (integer)

                case 0:
                    pass  # No validation needs to be performed on a 0 operand instruction as there are no operands to validate

                case 1:
                    self.__analyseSingleOperandInstruction(chadsemblyInstruction, beginningOfInstruction+1, instructionPool)

                case 2:
                    self.__analyseDoubleOperandInstruction(chadsemblyInstruction, beginningOfInstruction+1, instructionPool)


    def __semanticallyAnalyseInstructionPool(self: "SemanticAnalyser", instructionPool: InstructionPool) -> None:
        """Given an instruction pool, this method will perform the semantic analysis on the given instruction pool"""

        currentIndex: int = 0  # Initialise with 0 to begin iteration from start of instruction pool token stream

        while currentIndex < len(instructionPool.tokenStream):
            # As the number of tokens can change depending on what happens in the loop, 
            #   the number of tokens will need to be recalculated on each iteration
            # This is to ensure the indexable bounds are still being iterated within

            # If an Instruction token is encountered
            if instructionPool.tokenStream[currentIndex].tokenType == TypedToken.INSTRUCTION:

                self.__analyseInstruction(currentIndex, instructionPool)                

            currentIndex += 1  # Increment the index to move onto the next token

    def semanticAnalyse(self: "SemanticAnalyser") -> tuple:
        """The main method of the SemanticAnalyser class, combining all other methods needed to semantically analyse a stream of tokens"""

        self.__semanticallyAnalyseInstructionPool(self.__globalInstructionPool)

        for instructionPool in self.__instructionPools:

            self.__semanticallyAnalyseInstructionPool(self.__instructionPools[instructionPool])

        self.__getSemanticAnalysisErrors()

        return (self.__instructionPools, self.__globalInstructionPool)