"""
Module containing the 'CodeGenerator' class
"""

from operand import Operand
from binarystring import BinaryString
from keywords import KeyWords
from defaults import Defaults
from typedtoken import TypedToken
from symboltable import SymbolTable
from symboltableentry import SymbolTableEntry
from instructionpool import InstructionPool

class CodeGenerator:
    """
    -Class encapsulating all functionality required to translate a token stream into its corresponding chadsembly machine code equivalent
    """

    instructionPools: dict[str, InstructionPool]
    globalInstructionPool: InstructionPool
    configurationTable: dict[str, int]
    variablePromises: dict[int, str]
    orderingOfProcedures: tuple
    generatedChadsemblyCode: list[str]
    numberOfMachineOperationBits: int
    numberOfAddressingModeBits: int
    numberOfOperandBits: int
    totalNumberOfInstructionBits: int
    numberOfGeneralPurposeRegisters: int

    def __init__(self: "CodeGenerator", instructionPools: dict[str, InstructionPool], globalInstructionPool: InstructionPool, configurationTable: dict[str, int]) -> None:
        """Constructor for a `Lexer` object"""

        # The stream of tokens located in the local scopes of all procedures
        self.__instructionPools: dict[str, InstructionPool] = instructionPools

        # The token stream storing all global tokens (tokens not found within the scope of a procedure)
        self.__globalInstructionPool: InstructionPool = globalInstructionPool

        # The mapping storing "configuration option: configuration value" pairs which define how chadsembly code should be manipulated
        self.__configurationTable: dict[str, int] = configurationTable

        # A dictionary storing the indexes of variables within the generated code that need to be initialised with a value
        # Variables are allocated space in the generated code but are not initialised with a value
        # These variable initialisations must be performed once all the code has been generated
        # This can be achieved by storing the context of the variables that need to be initialised and resisting the generated code to initialise the variables
        # A "promise" in this context refers to a promise to initialise the variables at the given index with a value once all code was generated
        self.__variablePromises: dict[int, str] = {}

        # The fixed ordering of procedures that must be respected
        # It is critical this ordering is used whenever iterating over all procedures
        # Variable offsets are calculated based off of this ordering and so if it is not respected the generated code will be invalid
        self.__orderingOfProcedures: tuple = instructionPools.keys()

        # Will accumulate all of the generated chadsembly code
        self.__generatedChadsemblyCode: list[str] = []

        # Chadsembly machine code format related data
        # These were calculated and initialised as attributes so they may be accessible within every method and don't have to constantly be recalculated
        self.__numberOfMachineOperationBits: int = BinaryString.numberOfBits(KeyWords.NUMBER_OF_INSTRUCTIONS)
        self.__numberOfAddressingModeBits: int = BinaryString.numberOfBits(KeyWords.NUMBER_OF_ADDRESSING_MODES)
        self.__numberOfOperandBits: int = self.__calculateNumberOfOperandBits()
        self.__totalNumberOfInstructionBits: int = self.__numberOfMachineOperationBits + self.__numberOfAddressingModeBits + (2 * self.__numberOfOperandBits)
        self.__numberOfGeneralPurposeRegisters: int = configurationTable[Defaults.REGISTERS_CONFIGURATION_OPTION]

    def __wrapAround(self: "CodeGenerator", lowerBound: int, upperBound: int, value: int) -> int:
        """Method returning an integer, wrapping around from a given upper and lower bound, imitating integer overflowing"""

        # Iterate to constantly apply the operation until the value overflows
        # if a number is overflowing and wraps around, the value cannot be greater than the upperBound
        while value > upperBound:

            # To imitate wrapping around from the lower bound, we apply this operation:
            #   The difference between the value and upper bound is how much the number is overflowing by
            #   We add this to the lower (lowerBound - 1) to wrap around from the beginning. 
            #   The reason we add it to (lowerBound - 1) and not just the lowerBound is so it wraps around from the actual lowerBound
            value = (lowerBound - 1) + (value - upperBound)

        # Return the new, wrapped around value
        return value
    
    def __calculateNumberOfOperandBits(self: "CodeGenerator") -> int:
        """Will work out the minimum amount of bits required to cover all available memory addresses and registers so they may be accessed within an operand"""

        # The total registers is the general purpose registers + the special purpose registers
        numberOfRegisters: int = self.__configurationTable[Defaults.REGISTERS_CONFIGURATION_OPTION] + KeyWords.NUMBER_OF_SPECIAL_PURPOSE_REGISTERS

        # Total memory addresses can be grabbed from the configuration table
        numberOfMemoryAddresses: int = self.__configurationTable[Defaults.MEMORY_CONFIGURATION_OPTION]

        # Use whichever value is the greatest as the minimum value that should be used to access all available registers and memory addresses
        operandBits = BinaryString.numberOfBits(numberOfMemoryAddresses) if numberOfMemoryAddresses > numberOfRegisters else BinaryString.numberOfBits(numberOfRegisters)

        return operandBits + 1  # +1 so as to account for the sign bit

    def __countNumberOfInstructions(self: "CodeGenerator", instructionPool: InstructionPool) -> int:
        """Count the number of instructions (statements) in a given instruction pool"""

        numberOfInstructions: int = 0  # Initialise to 0 to begin counting instructions

        for token in instructionPool.tokenStream:  # Iterate through each token found within the instruction pool

            if token.tokenType == TypedToken.INSTRUCTION:  # If an instruction is encountered...

                numberOfInstructions += 1  # Increment the number of instructions counter

        return numberOfInstructions  # Return the total amount of instructions to the caller                 

    def __countNumberOfVariables(self: "CodeGenerator", instructionPool: InstructionPool) -> int:
        """Count the number of variables (labels declared with the DAT assembler directive) in a given instruction pool"""

        numberOfVariables: int = 0  # Initialise to 0 to begin counting variables
        symbolEntry: str

        # Iterate through each symbol (label) found within the instruction pool's symbol table
        for symbolEntry in instructionPool.symbolTable.getLabels():

            # If the symbol is a symbol for a variable label...
            if instructionPool.symbolTable.get(symbolEntry).labelType == SymbolTable.VARIABLE_LABEL:

                numberOfVariables += 1  # Increment the number of variables counter

        return numberOfVariables  # Return the total amount of variables to the caller

    def __updateBranchLabelAddresses(self, instructionPool: InstructionPool, currentOffset: int):
        """Update the local branch labels in a procedure to store the new correct jump address to branch to"""
     
        symbolEntry: SymbolTableEntry
        for symbol in instructionPool.symbolTable.getLabels(): # Iterate over each symbol in the symbol table

            # Access the symbolic data for the given symbol
            symbolEntry = instructionPool.symbolTable.get(symbol)

            # If the symbol is a branch label...
            if symbolEntry.labelType == SymbolTable.BRANCH_LABEL:

                # Add the current offset of the code pool
                # This will update the jump address to now be relative to the starting point of the program
                # Not the starting point of the procedure it is located in
                symbolEntry.labelValue += currentOffset

    def __pregenerateProcedureLabelIndexes(self: "CodeGenerator") -> None:
        """Will pre-generate the indexes of the beginning of all procedures found within the chadsembly source code file
        The global symbol table will be updated to reflect these changes
        This allows for procedure labels to directly be mapped into its index within the generated code pool
        This is a great example of thinking ahead within the code"""

        # The offset is how far from the origin (index 0) we currently are
        # The number of instructions and variables for a particular instruction pool can be added to the offset 
        #   to calculate where the beginning of the next instruction pool would be within the generate chadsembly code
        # This is why it is imperative that the order in which procedures are processed in is consistent
        # If it isn't consistent then the wrong offset will be used for different instruction pools, resulting in the generation of an invalid program
        currentProcedureOffset = self.__countNumberOfInstructions(self.__globalInstructionPool) + self.__countNumberOfVariables(self.__globalInstructionPool)

        for procedureLabel in self.__orderingOfProcedures:  # Iterate through the label (identifier) of every procedure found within the source code
            
            procedureInstructionPool = self.__instructionPools[procedureLabel]  # Grab the instruction pool for the procedure

            # Update the jump addresses of all branch labels within the instruction pool
            self.__updateBranchLabelAddresses(procedureInstructionPool, currentProcedureOffset)

            # Update the label value to store the pre-calculated index of where it will be stored in memory
            self.__globalInstructionPool.symbolTable.get(procedureLabel).labelValue = currentProcedureOffset

            # Recalculate the new offset of the procedure to ensure the next offset used is correct for the current instruction pool
            currentProcedureOffset += self.__countNumberOfInstructions(procedureInstructionPool) + self.__countNumberOfVariables(procedureInstructionPool)

    def __pregenerateVariableLabelIndexesForInstructionPool(self: "CodeGenerator", instructionPool: InstructionPool, currentOffset) -> int:
        """Will pregenerate the indexes of all variables found within a particular instruction pool
        The scoping of variables are respected and so will follow basic scoping precedent
        A promise to initialise each variable will be made, these promises will be resolved once all code has been generated"""

        # Update the current offset from the origin by adding the number of statements within the current instruction pool to the offset
        currentOffset += self.__countNumberOfInstructions(instructionPool)

        # Iterate through each symbol found within the symbol table of the given instruction pool
        for symbol in instructionPool.symbolTable.getLabels():

            symbolEntry: SymbolTableEntry = instructionPool.symbolTable.get(symbol)  # Get the symbol from the symbol table
            
            if symbolEntry.labelType == SymbolTable.VARIABLE_LABEL:  # If a variable label is encountered...

                # Create a promise to initialise the variable at the given offset with the given value
                self.__variablePromises[currentOffset] = symbolEntry.labelValue
                symbolEntry.labelValue = currentOffset  # Update the symbol table to store the current index mapping of the label
                currentOffset += 1  # Increment the offset to store the position of the next address for the variable

        return currentOffset  # Return the offset to the caller

    def __pregenerateVariableLabelIndexes(self: "CodeGenerator") -> None:
        """Will pregenerate the indexes of all variables found within a chadsembly source code file"""

        # Initialise the offset to begin from 0 - the origin
        currentOffset = self.__pregenerateVariableLabelIndexesForInstructionPool(self.__globalInstructionPool, 0)

        # Iterate through the label (identifier) of every procedure found within the source code
        for procedureLabel in self.__orderingOfProcedures:

            # Pregenerate the indexes of the variables to be found within the generated source chadsembly source code
            currentOffset = self.__pregenerateVariableLabelIndexesForInstructionPool(self.__instructionPools[procedureLabel], currentOffset)

    def __resolveLabel(self: "CodeGenerator", labelToken: TypedToken, instructionPool: InstructionPool) -> int:
        """Resolve the label, a label will map to an underlying address in the generated code
        This method is responsible for getting that value"""

        labelSymbol: SymbolTableEntry = instructionPool.symbolTable.get(labelToken.tokenValue)  # Get the symbol for label

        if labelSymbol is Defaults.NULL:  # If the label could not be found in the local scope then it is a global variable

            return self.__globalInstructionPool.symbolTable.get(labelToken.tokenValue).labelValue  # Return the address of the global variable

        return labelSymbol.labelValue  # Return the address of the local variable

    def __resolveValue(self: "CodeGenerator", valueToken: TypedToken, instructionPool: InstructionPool) -> int:
        """Will return the value as an integer found in the value token"""

        return int(valueToken.tokenValue)  # Cast the token value to an integer (the integer is stored as a string when it is a token value)

    def __resolveRegister(self: "CodeGenerator", registerToken: TypedToken, instructionPool: InstructionPool) -> None:
        """Resolve the register by determining if it is a special purpose register or general purpose register then calculate the appropriate denary integer from it"""

        if registerToken.tokenValue in KeyWords.SPECIAL_PURPOSE_REGISTERS:  # If it is a special purpose register

            # Special purpose registers will begin from just after the general purpose registers
            # This is so general purpose registers have a natural fit for their denary mapping
            # For example: general purpose register 1 will map to a denary integer of 1 and so on
            return self.__numberOfGeneralPurposeRegisters + KeyWords.SPECIAL_PURPOSE_REGISTERS_OFFSET[registerToken.tokenValue]

        # If not then we can assume it is a general purpose register
        # To ensure the register is within the available bounds of usable registers, we will mod the register number by the number of registers + 1
        # return int(registerToken.tokenValue) % (self.__numberOfGeneralPurposeRegisters + 1)
        return self.__wrapAround(1, self.__numberOfGeneralPurposeRegisters, int(registerToken.tokenValue))

    def __resolveOperand(self: "CodeGenerator", operandToken: Operand, instructionPool: InstructionPool) -> int:
        """Given an operand token, will determine what type it is then act accordingly in order to return a denary integer that represents the token"""

        match operandToken.operandValue.tokenType:  # Switch statement with a match target of a token type (an integer)

            case TypedToken.LABEL:  # In the case where it is a label

                return self.__resolveLabel(operandToken.operandValue, instructionPool)  # Resolve the label

            case TypedToken.VALUE:  # In the case where it is a value

                return self.__resolveValue(operandToken.operandValue, instructionPool)  # Resolve the value

            case TypedToken.REGISTER:  # In the case where it is a register

                return self.__resolveRegister(operandToken.operandValue, instructionPool)  # Resolve the register

    def __convertToChadsemblyMachineCode(self: "CodeGenerator", chadsemblyInstruction: TypedToken, sourceOperand: Operand, destinationOperand: Operand, instructionPool: InstructionPool) -> str:

        instructionOpcode: int = KeyWords.INSTRUCTION_SET[chadsemblyInstruction.tokenValue]  # Get the denary opcode for the instruction
        addressingModeOpcode: int = KeyWords.ADDRESSING_MODE_TO_OPCODE[sourceOperand.addressingMode.tokenValue]  # Get the denary opcode for the addressing mode

        # Instantiate a string and add the machine instruction and addressing mode opcodes in binary format
        formattedChadsemblyInstruction: str = BinaryString.unsignedInteger(instructionOpcode, self.__numberOfMachineOperationBits) + \
                                     BinaryString.unsignedInteger(addressingModeOpcode, self.__numberOfAddressingModeBits)
        
        sourceOperandValue: int = self.__resolveOperand(sourceOperand, instructionPool)  # Get the denary value for the source operand

        # Generate a signed binary string from the source operand value
        formattedChadsemblyInstruction += BinaryString.signedInteger(sourceOperandValue, self.__numberOfOperandBits)

        destinationOperandValue: int = self.__resolveOperand(destinationOperand, instructionPool)  # Get the denary value for the destination operand

        # Generate a signed binary string from the destination operand value
        formattedChadsemblyInstruction += BinaryString.signedInteger(destinationOperandValue, self.__numberOfOperandBits)

        return formattedChadsemblyInstruction  # Return the formatted instruction as a binary string

    def __generateChadsemblyInstruction(self: "CodeGenerator", beginningOfInstruction: int, instructionPool: InstructionPool) -> str:
        """Method responsible for invoking the generation of the chadsembly instruction
        It will ensure before an instruction is generated all relevant data is present so it may be formatted correctly"""

        chadsemblyInstruction: TypedToken = instructionPool.tokenStream[beginningOfInstruction]  # Grab the chadsembly instruction

        # Grab the number of operands the specified instruction should have
        numberOfInstructionOperands: int = KeyWords.NUMBER_OF_INSTRUCTION_OPERANDS[chadsemblyInstruction.tokenValue]

        # Initialise a default, 0 padded operand that will be the placeholder for empty operands
        defaultOperand: Operand = Operand(TypedToken(4, '%', -1, -1), TypedToken(3, '0', -1, -1))

        match numberOfInstructionOperands:  # Switch case statement with a match target of an integer

            case 0:  # In the case where the instruction has 0 operands

                # Return the generation of the formatted instruction
                # Despite the instruction having 0 operands, the defaultOperand was passed in twice to fill the empty operands
                # As chadsembly operates with fixed-length instructions (not dynamic length instructions)
                # Both operands must be present even if they are not used
                return self.__convertToChadsemblyMachineCode(chadsemblyInstruction, 
                    defaultOperand,
                    defaultOperand,
                    instructionPool)

            case 1:  # In the case where the instruction has 2 operands

                # Return the generation of the formatted instruction
                # Pass in 1 default operand to make up for the missing second operand
                return self.__convertToChadsemblyMachineCode(chadsemblyInstruction, 
                    # Calculate the locations of the addressing mode and value of the first operand relative to the instruction
                    Operand(instructionPool.tokenStream[beginningOfInstruction+1], instructionPool.tokenStream[beginningOfInstruction+2]),
                    defaultOperand,
                    instructionPool)

            case 2:
                # Return the generation of the formatted instruction
                # Calculate the locations of the addressing modes and values of the first operand relative to the instruction

                return self.__convertToChadsemblyMachineCode(chadsemblyInstruction, 
                    Operand(instructionPool.tokenStream[beginningOfInstruction+1], instructionPool.tokenStream[beginningOfInstruction+2]),
                    Operand(instructionPool.tokenStream[beginningOfInstruction+4], instructionPool.tokenStream[beginningOfInstruction+5]),
                    instructionPool)

    def __generateCodeForInstructionPool(self: "CodeGenerator", instructionPool: InstructionPool) -> None:
        """Given a token stream, will generate the corresponding chadsembly machine code for it"""

        # A precondition for this method is that the procedure and variable indexes were pregenerated
        # Since this method will actually generate the chadsembly machine code, it will map labels to its index within the generated code
        # And so it is required the indexes were pregenerated otherwise the program will be assembled wrongly

        currentIndex: int = 0  # Initialise with 0 to begin iteration from the beginning
        numberOfTokens: int = len(instructionPool.tokenStream)  # Cache the number of tokens in a variable to avoid recomputing it on every iteration of the loop

        while currentIndex < numberOfTokens:  # Only iterate while in the indexable bounds of the token stream

            match instructionPool.tokenStream[currentIndex].tokenType:  # Switch statement with a match target of the token type (an integer)

                case TypedToken.INSTRUCTION:  # In the case where it is an instruction

                    # Generate a formatted chadsembly instruction and append it to the generated code pool
                    self.__generatedChadsemblyCode.append(self.__generateChadsemblyInstruction(currentIndex, instructionPool))

            currentIndex += 1  # Increment the loop control variable to move onto the next token in the iteration

        for _ in range(self.__countNumberOfVariables(instructionPool)):  # Only iterate n amount of times where n is the number of variables

            # Append a non-initialised variable to the instruction pool
            # These non-initialised variables will be initialised with their values once all code has been generated
            # The variables (and all other values) will share the same amount of bits as an instruction
            self.__generatedChadsemblyCode.append('0'*self.__totalNumberOfInstructionBits)

    def __resolveVariablePromises(self: "CodeGenerator") -> None:
        """Will resolve all variable initialisation promises"""

        # A precondition for this method is that the promises were all pregenerated and the code also generated

        for index in self.__variablePromises:  # Iterate through each promise

            self.__generatedChadsemblyCode[index] = BinaryString.signedInteger(int(self.__variablePromises[index]), self.__totalNumberOfInstructionBits)

    def generateCode(self: "CodeGenerator") -> tuple:
        """The main method of the Codegenerator class, wrapping all other methods needed to convert a series of instruction pools into its corresponding chadsembly machine code"""

        self.__pregenerateProcedureLabelIndexes()  # Pregenerate the indexes of all procedures
        self.__pregenerateVariableLabelIndexes()  # Pregenerate the indexes of all variables

        # Since the precondition of all procedure and variable indexes being pregenerated is now met
        # We can now generate the code for the instruction pools
        self.__generateCodeForInstructionPool(self.__globalInstructionPool)  # Generate the code for the global instruction pool first

        for instructionPool in self.__orderingOfProcedures:  # Then generate the code for all following instruction pools in the specified order

            self.__generateCodeForInstructionPool(self.__instructionPools[instructionPool])  # Generate the code for the instruction pool

        # Since all preconditions for the method have been met
        # The promises and code have all been generated up to this point in the program
        # And so the promises can now be resolved
        self.__resolveVariablePromises()        

        return (self.__configurationTable, self.__generatedChadsemblyCode, self.__numberOfMachineOperationBits, 
                self.__numberOfAddressingModeBits, self.__numberOfOperandBits, self.__totalNumberOfInstructionBits)