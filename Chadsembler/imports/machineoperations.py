"""
Module containing the 'MachineOperations' class
"""

import sys
from binarystring import BinaryString
from keywords import KeyWords
from colour import Colour

class MachineOperations:
    """
    -Class encapsulating all machine operations (the actual instruction)
    -Each machine operation is modularised into its own method
    -A dictionary mapping the opcode to the machine operation will be accessible as a static member
    -This is to ensure the quick access of specific machine operations from their opcode
    -Each machine operation also takes a source operand and destination operand, regardless whether they use it or not
    -This is to ensure each machine operation is uniform and consistent
    """

    # --Class Members / Object Attributes
    memoryPool: dict[int, str]
    totalNumberOfBits: int
    numberOfGeneralPurposeRegisters: int

    # --Object Methods
    def __init__(self: "MachineOperations", memoryPool: dict[int, str], totalNumberOfBits: int, numberOfGeneralPurposeRegisters: int):
        """Constructor for a `MachineOperations` object"""

        # The memory pool the instructions can manipulate
        self.__memoryPool: dict[int, str] = memoryPool

        # The number of bits used for an instruction / the width of the address bus in the VirtualMachine
        self.__totalNumberOfBits: int = totalNumberOfBits

        # The total number of registers available for use
        # Important for when calculating the underlying address of special-purpose registers which begin from after
        #   the general purpose registers
        # Registers have a negative memory address under the hood
        self.__numberOfGeneralPurposeRegisters: int = numberOfGeneralPurposeRegisters

    def HLT(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Suspends the execution of the program"""

        sys.exit(0)  # Exit the whole program

    def ADD(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Add the value in the source operand onto the value in the destination operand"""

        # Calculate the new value by adding the source operand to the denary value of the value stored at the destination operand
        newValue: int = BinaryString.readSignedInteger(self.__memoryPool[destinationOperand]) + sourceOperand

        # Update the value at the destination operand to store the new value (the result of adding both numbers together)
        self.__memoryPool[destinationOperand] = BinaryString.signedInteger(newValue, self.__totalNumberOfBits)

    def SUB(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Subtract the value in the source operand from the value in the destination operand"""

        # Calculate the new value by subtracting the source operand to the denary value of the value stored at the destination operand
        newValue: int = BinaryString.readSignedInteger(self.__memoryPool[destinationOperand]) - sourceOperand

        # Update the value at the destination operand to store the new value (the result of subtracting both numbers from each other)
        self.__memoryPool[destinationOperand] = BinaryString.signedInteger(newValue, self.__totalNumberOfBits)

    def STA(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Store the value in the destination operand into the source operand"""

        # Reassign the value addressed by the source operand to now store the value addressed by the destination operand 
        #    - copy the value in the source operand to the destination operand
        self.__memoryPool[sourceOperand] = self.__memoryPool[destinationOperand]

    def NOP(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Perform an empty operation, do nothing - wastes a clock cycle"""

        pass  # Do nothing

    def LDA(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Load the value in the source operand onto the destination operand"""

        # Copy the value in the source operand into the address in the destination operand
        self.__memoryPool[destinationOperand] = BinaryString.signedInteger(sourceOperand, self.__totalNumberOfBits)

    def BRA(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Always branch to the address in the source operand, regardless what value is in the destination operand"""

        # Calculate the underlying address for the special-purpose Program Counter register
        programCounterAddress: int = (KeyWords.SPECIAL_PURPOSE_REGISTERS_OFFSET[KeyWords.PROGRAM_COUNTER] + self.__numberOfGeneralPurposeRegisters) * -1

        # Update the program counter to store the address in the source operand (the new point to continue executing the program from)
        self.__memoryPool[programCounterAddress] = BinaryString.signedInteger(sourceOperand, self.__totalNumberOfBits)

    def BRZ(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Branch to the address in the source operand if the value in the destination operand == 0"""

        # Calculate the underlying address for the special-purpose Program Counter register
        programCounterAddress: int = (KeyWords.SPECIAL_PURPOSE_REGISTERS_OFFSET[KeyWords.PROGRAM_COUNTER] + self.__numberOfGeneralPurposeRegisters) * -1

        if BinaryString.readSignedInteger(self.__memoryPool[destinationOperand]) == 0:  # If the value in the destination is zero

            # Update the program counter to store the address in the source operand (the new point to continue executing the program from)                
            self.__memoryPool[programCounterAddress] = BinaryString.signedInteger(sourceOperand, self.__totalNumberOfBits)

        # If not then do nothing and leave the program counter untouched - effectively not branching

    def BRP(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Branch to the address in the source operand if the value in the destination operand >= 0"""

        # Calculate the underlying address for the special-purpose Program Counter register
        programCounterAddress: int = (KeyWords.SPECIAL_PURPOSE_REGISTERS_OFFSET[KeyWords.PROGRAM_COUNTER] + self.__numberOfGeneralPurposeRegisters) * -1

        if BinaryString.readSignedInteger(self.__memoryPool[destinationOperand]) > -1:  # If the value in the destination is zero
            # As we're working with integers, > -1 is the same as and more efficient than >= 0

            # Update the program counter to store the address in the source operand (the new point to continue executing the program from)
            self.__memoryPool[programCounterAddress] = BinaryString.signedInteger(sourceOperand, self.__totalNumberOfBits)

        # If not then do nothing and leave the program counter untouched - effectively not branching

    def INP(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Gather input and store it in the source operand"""

        try:
            # Attempt to get input from the terminal and interpret it as an integer
            # If it could not be interpreted as an integer then python will raise a "ValueError"
            # Output the input indicator in green
            terminalInput: int = int(input(f"{Colour.GREEN}\n>>>{Colour.RESET}"))

            # Update the address stored in the source operand to now store the input gathered from the terminal
            self.__memoryPool[sourceOperand] = BinaryString.signedInteger(terminalInput, self.__totalNumberOfBits)

        except ValueError:  # If the input could not be interpreted as an integer

            # Output, in red, that there has been a run-time error and suspend execution of the program
            sys.exit(f"{Colour.RED}Runtime Error: Non-inferrable integer value passed in as input{Colour.RESET}")

    def OUT(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Output the value in the source operand"""

        print(sourceOperand)  # Output the integer value

    def OUTC(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Output the value mapped to its ASCII character in the source operand"""

        print(chr(sourceOperand), end='')  # Output the integer value encoded as a character

    def OUTB(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Output the binary held in the memory address / register in the source operand"""

        print(sourceOperand)  # Output the binary

    def AND(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Logical AND operation on the value in the destination operand with a mask of the source operand"""

        # Calculate the new value by performing a bitwise AND operation on the value addressed by the destination operand with a mask of the value in the source operand
        newValue: int = BinaryString.readSignedInteger(self.__memoryPool[destinationOperand]) & sourceOperand

        # Update the value at the destination operand to store the new value (the result of performing a bitwise AND operation with both values)
        self.__memoryPool[destinationOperand] = BinaryString.signedInteger(newValue, self.__totalNumberOfBits)

    def OR(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Logical AND operation on the value in the destination operand with a mask of the source operand"""

        # Calculate the new value by performing a bitwise OR operation on the value addressed by the destination operand with a mask of the value in the source operand
        newValue: int = BinaryString.readSignedInteger(self.__memoryPool[destinationOperand]) | sourceOperand

        # Update the value at the destination operand to store the new value (the result of performing a bitwise OR operation with both values)
        self.__memoryPool[destinationOperand] = BinaryString.signedInteger(newValue, self.__totalNumberOfBits)

    def NOT(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Logical NOT operation on the value in the source operand, storing it in the destination operand"""

        # Calculate the new value by performing a bitwise NOT operation on the value in the source operand
        newValue: int = ~sourceOperand

        # Update the value at the destination operand to store the new value (the result of performing a bitwise NOT operation)
        self.__memoryPool[destinationOperand] = BinaryString.unsignedInteger(newValue, self.__totalNumberOfBits)

    def XOR(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Logical XOR operation on the value in the destination operand with a mask of the source operand"""

        # Calculate the new value by performing a bitwise XOR operation on the value addressed by the destination operand with a mask of the value in the source operand
        newValue: int = BinaryString.readSignedInteger(self.__memoryPool[destinationOperand]) ^ sourceOperand

        # Update the value at the destination operand to store the new value (the result of performing a bitwise XOR operation with both values)
        self.__memoryPool[destinationOperand] = BinaryString.signedInteger(newValue, self.__totalNumberOfBits)

    def LSL(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Bitwise Logical Left Shift on the value in the destination operand n amount of times where n is the value in the source operand"""

        # Calculate the underlying address for the special-purpose Flags register
        flagRegisterAddress: int = (KeyWords.SPECIAL_PURPOSE_REGISTERS_OFFSET[KeyWords.FLAGS_REGISTER] + self.__numberOfGeneralPurposeRegisters) * -1

        # Store the new flag value after operations, initialise with the existing value held in the Flags register
        newFlagValue: str = self.__memoryPool[flagRegisterAddress][-1]

        # Store the new destination operand value, initialise with the existing value held in the the address in the destination operand
        newValue: str = self.__memoryPool[destinationOperand]

        # Count-controlled loop, performed "source operand" amount of times - carry out the operation by the amount of times specified in the "source operand"
        for count in range(sourceOperand):

            # The newFlagValue variable will store the carry bit resulting from the shift
            # The newValue variable will store the shifted value
            # Perform the shift on the current value and store the corresponding results in the corresponding variables
            newFlagValue, newValue = BinaryString.logicalShiftLeft(newValue)

        # Update the Flags register to store the final new flags value from performing the shift
        self.__memoryPool[flagRegisterAddress] = BinaryString.padBinary(newFlagValue, self.__totalNumberOfBits-1)

        # Update the address stored in the destination operand to store the final value from performing the shift
        self.__memoryPool[destinationOperand] = newValue

    def LSR(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Bitwise Logical Right Shift on the value in the destination operand n amount of times where n is the value in the source operand"""

        # Calculate the underlying address for the special-purpose Flags register
        flagRegisterAddress: int = (KeyWords.SPECIAL_PURPOSE_REGISTERS_OFFSET[KeyWords.FLAGS_REGISTER] + self.__numberOfGeneralPurposeRegisters) * -1

        # Store the new flag value after operations, initialise with the existing value held in the Flags register
        newFlagValue: str = self.__memoryPool[flagRegisterAddress][-1]

        # Store the new destination operand value, initialise with the existing value held in the the address in the destination operand
        newValue: str = self.__memoryPool[destinationOperand]

        # Count-controlled loop, performed "source operand" amount of times - carry out the operation by the amount of times specified in the "source operand"
        for count in range(sourceOperand):

            # The newFlagValue variable will store the carry bit resulting from the shift
            # The newValue variable will store the shifted value
            # Perform the shift on the current value and store the corresponding results in the corresponding variables
            newFlagValue, newValue = BinaryString.logicalShiftRight(newValue)

        # Update the Flags register to store the final new flags value from performing the shift 
        self.__memoryPool[flagRegisterAddress] = BinaryString.padBinary(newFlagValue, self.__totalNumberOfBits-1)

        # Update the address stored in the destination operand to store the final value from performing the shift
        self.__memoryPool[destinationOperand] = newValue  

    def ASL(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Bitwise Arithmetic Left Shift on the value in the destination operand n amount of times where n is the value in the source operand"""

        # Calculate the underlying address for the special-purpose Flags register
        flagRegisterAddress: int = (KeyWords.SPECIAL_PURPOSE_REGISTERS_OFFSET[KeyWords.FLAGS_REGISTER] + self.__numberOfGeneralPurposeRegisters) * -1

        # Store the new flag value after operations, initialise with the existing value held in the Flags register
        newFlagValue: str = self.__memoryPool[flagRegisterAddress][-1]

        # Store the new destination operand value, initialise with the existing value held in the the address in the destination operand
        newValue: str = self.__memoryPool[destinationOperand]

        # Count-controlled loop, performed "source operand" amount of times - carry out the operation by the amount of times specified in the "source operand"
        for count in range(sourceOperand):

            # The newFlagValue variable will store the carry bit resulting from the shift
            # The newValue variable will store the shifted value
            # Perform the shift on the current value and store the corresponding results in the corresponding variables
            newFlagValue, newValue = BinaryString.arithmeticShiftLeft(newValue)

        # Update the Flags register to store the final new flags value from performing the shift 
        self.__memoryPool[flagRegisterAddress] = BinaryString.padBinary(newFlagValue, self.__totalNumberOfBits-1)

        # Update the address stored in the destination operand to store the final value from performing the shift
        self.__memoryPool[destinationOperand] = newValue  

    def ASR(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Bitwise Arithmetic Right Shift on the value in the destination operand n amount of times where n is the value in the source operand"""

        # Calculate the underlying address for the special-purpose Flags register
        flagRegisterAddress: int = (KeyWords.SPECIAL_PURPOSE_REGISTERS_OFFSET[KeyWords.FLAGS_REGISTER] + self.__numberOfGeneralPurposeRegisters) * -1

        # Store the new flag value after operations, initialise with the existing value held in the Flags register
        newFlagValue: str = self.__memoryPool[flagRegisterAddress][-1]

        # Store the new destination operand value, initialise with the existing value held in the the address in the destination operand
        newValue: str = self.__memoryPool[destinationOperand]

        # Count-controlled loop, performed "source operand" amount of times - carry out the operation by the amount of times specified in the "source operand"
        for count in range(sourceOperand):

            # The newFlagValue variable will store the carry bit resulting from the shift
            # The newValue variable will store the shifted value
            # Perform the shift on the current value and store the corresponding results in the corresponding variables
            newFlagValue, newValue = BinaryString.arithmeticShiftRight(newValue)

        # Update the Flags register to store the final new flags value from performing the shift 
        self.__memoryPool[flagRegisterAddress] = BinaryString.padBinary(newFlagValue, self.__totalNumberOfBits-1)

        # Update the address stored in the destination operand to store the final value from performing the shift
        self.__memoryPool[destinationOperand] = newValue  

    def CSL(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Bitwise Circular Left Shift on the value in the destination operand n amount of times where n is the value in the source operand"""

        # As a Circular Shift without any carry does not produce a carry bit or use a carry bit, the flags register wont need to be accessed at all
        # Store the new destination operand value, initialise with the existing value held in the the address in the destination operand
        newValue: str = self.__memoryPool[destinationOperand]  

        # Count-controlled loop, performed "source operand" amount of times - carry out the operation by the amount of times specified in the "source operand"
        for count in range(sourceOperand):

            # Perform the shift on the current value and store new shifted value in the appropriate variable
            newValue = BinaryString.circularShiftLeft(newValue)

        # Update the address stored in the destination operand to store the final value from performing the shift
        self.__memoryPool[destinationOperand] = newValue

    def CSR(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Bitwise Circular Right Shift on the value in the destination operand n amount of times where n is the value in the source operand"""

        # As a Circular Shift without any carry does not produce a carry bit or use a carry bit, the flags register wont need to be accessed at all
        # Store the new destination operand value, initialise with the existing value held in the the address in the destination operand
        newValue: str = self.__memoryPool[destinationOperand]  

        # Count-controlled loop, performed "source operand" amount of times - carry out the operation by the amount of times specified in the "source operand"
        for count in range(sourceOperand):  

            # Perform the shift on the current value and store new shifted value in the appropriate variable
            newValue = BinaryString.circularShiftRight(newValue)

        # Update the address stored in the destination operand to store the final value from performing the shift
        self.__memoryPool[destinationOperand] = newValue

    def CSLC(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Bitwise Circular Left Shift With Carry on the value in the destination operand n amount of times where n is the value in the source operand"""

        # Calculate the underlying address for the special-purpose Flags register
        flagRegisterAddress: int = (KeyWords.SPECIAL_PURPOSE_REGISTERS_OFFSET[KeyWords.FLAGS_REGISTER] + self.__numberOfGeneralPurposeRegisters) * -1

        # Store the new flag value after operations, initialise with the existing value held in the Flags register
        newFlagValue: str = self.__memoryPool[flagRegisterAddress][-1]

        # Store the new destination operand value, initialise with the existing value held in the the address in the destination operand
        newValue: str = self.__memoryPool[destinationOperand]  

        # Count-controlled loop, performed "source operand" amount of times - carry out the operation by the amount of times specified in the "source operand"
        for count in range(sourceOperand):

            # The newFlagValue variable will store the carry bit resulting from the shift
            # The newValue variable will store the shifted value
            # Perform the shift on the current value and store the corresponding results in the corresponding variables
            newFlagValue, newValue = BinaryString.circularShiftLeftWithCarry(newValue, newFlagValue)

        # Update the Flags register to store the final new flags value from performing the shift
        self.__memoryPool[flagRegisterAddress] = BinaryString.padBinary(newFlagValue, self.__totalNumberOfBits-1)

        # Update the address stored in the destination operand to store the final value from performing the shift
        self.__memoryPool[destinationOperand] = newValue

    def CSRC(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Bitwise Circular Right Shift With Carry on the value in the destination operand n amount of times where n is the value in the source operand"""

        # Calculate the underlying address for the special-purpose Flags register
        flagRegisterAddress: int = (KeyWords.SPECIAL_PURPOSE_REGISTERS_OFFSET[KeyWords.FLAGS_REGISTER] + self.__numberOfGeneralPurposeRegisters) * -1

        # Store the new flag value after operations, initialise with the existing value held in the Flags register
        newFlagValue: str = self.__memoryPool[flagRegisterAddress][-1]

        # Store the new destination operand value, initialise with the existing value held in the the address in the destination operand
        newValue: str = self.__memoryPool[destinationOperand]

        # Count-controlled loop, performed "source operand" amount of times - carry out the operation by the amount of times specified in the "source operand"
        for count in range(sourceOperand):

            # The newFlagValue variable will store the carry bit resulting from the shift
            # The newValue variable will store the shifted value

            # Perform the shift on the current value and store the corresponding results in the corresponding variables
            newFlagValue, newValue = BinaryString.circularShiftRightWithCarry(newValue, newFlagValue)

        # Update the Flags register to store the final new flags value from performing the shift 
        self.__memoryPool[flagRegisterAddress] = BinaryString.padBinary(newFlagValue, self.__totalNumberOfBits-1)

        # Update the address stored in the destination operand to store the final value from performing the shift
        self.__memoryPool[destinationOperand] = newValue

    def CALL(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Call a procedure by branching to the address of the procedure stored in the source operand
           Will also update the Return Register to store the address of the current instruction to return to"""

        # Calculate the underlying address for the special-purpose Program Counter register
        programCounterAddress: int = (KeyWords.SPECIAL_PURPOSE_REGISTERS_OFFSET[KeyWords.PROGRAM_COUNTER] + self.__numberOfGeneralPurposeRegisters) * -1

        # Calculate the underlying address for the special-purpose Return Register
        returnRegisterAddress: int = (KeyWords.SPECIAL_PURPOSE_REGISTERS_OFFSET[KeyWords.RETURN_REGISTER] + self.__numberOfGeneralPurposeRegisters) * -1

        # Copy the address in the Program Counter to the Return Register to store the point of execution to return to once the end of the procedure is reached
        self.__memoryPool[returnRegisterAddress] = self.__memoryPool[programCounterAddress]

        # Update the program counter to store the address in the Source Operand (the new point to continue executing the program from - the beginning of the procedure)
        self.__memoryPool[programCounterAddress] = BinaryString.signedInteger(sourceOperand, self.__totalNumberOfBits)

    def RET(self: "MachineOperations", sourceOperand: int, destinationOperand: int) -> None:
        """Return from a procedure by branching to the value held in the return register"""

        # Calculate the underlying address for the special-purpose Program Counter register
        programCounterAddress: int = (KeyWords.SPECIAL_PURPOSE_REGISTERS_OFFSET[KeyWords.PROGRAM_COUNTER] + self.__numberOfGeneralPurposeRegisters) * -1

        # Calculate the underlying address for the special-purpose Return Register
        returnRegisterAddress: int = (KeyWords.SPECIAL_PURPOSE_REGISTERS_OFFSET[KeyWords.RETURN_REGISTER] + self.__numberOfGeneralPurposeRegisters) * -1

        # Update the program counter to store the address in the Return Register (the new point to continue executing the program from - the point where the procedure was called from)
        self.__memoryPool[programCounterAddress] = self.__memoryPool[returnRegisterAddress]

    # --Static Members (Belong to the class and not an individual class instance)

    # The dictionary mapping opcodes to the corresponding machine operation
    # The opcode determined by the instruction set mapping in the keywords module is used instead of constant values
    # This is to ensure the correct addressing mode is used and also to ensure the modularity of the keywords module
    # Changes made to the keywords module should be reflected in the whole program rather than having to rewrite the whole program to reflect a change
    # If constant values were used here then in the case where an instruction opcode is changed, 
    #   this module will also have to be changed rather than only just changing the keywords module (the module that stores the actual opcode-instruction mapping)
    instructionMapping: dict[int, function] = {
        KeyWords.INSTRUCTION_SET[KeyWords.HLT]: HLT,
        KeyWords.INSTRUCTION_SET[KeyWords.ADD]: ADD,
        KeyWords.INSTRUCTION_SET[KeyWords.SUB]: SUB,
        KeyWords.INSTRUCTION_SET[KeyWords.STA]: STA,
        KeyWords.INSTRUCTION_SET[KeyWords.NOP]: NOP,
        KeyWords.INSTRUCTION_SET[KeyWords.LDA]: LDA,
        KeyWords.INSTRUCTION_SET[KeyWords.BRA]: BRA,
        KeyWords.INSTRUCTION_SET[KeyWords.BRZ]: BRZ,
        KeyWords.INSTRUCTION_SET[KeyWords.BRP]: BRP,
        KeyWords.INSTRUCTION_SET[KeyWords.INP]: INP,
        KeyWords.INSTRUCTION_SET[KeyWords.OUT]: OUT,
        KeyWords.INSTRUCTION_SET[KeyWords.OUTC]: OUTC,
        KeyWords.INSTRUCTION_SET[KeyWords.OUTB]: OUTB,
        KeyWords.INSTRUCTION_SET[KeyWords.AND]: AND,
        KeyWords.INSTRUCTION_SET[KeyWords.OR]: OR,
        KeyWords.INSTRUCTION_SET[KeyWords.NOT]: NOT,
        KeyWords.INSTRUCTION_SET[KeyWords.XOR]: XOR,
        KeyWords.INSTRUCTION_SET[KeyWords.LSL]: LSL,
        KeyWords.INSTRUCTION_SET[KeyWords.LSR]: LSR,
        KeyWords.INSTRUCTION_SET[KeyWords.ASL]: ASL,
        KeyWords.INSTRUCTION_SET[KeyWords.ASR]: ASR,
        KeyWords.INSTRUCTION_SET[KeyWords.CSL]: CSL,
        KeyWords.INSTRUCTION_SET[KeyWords.CSR]: CSR,
        KeyWords.INSTRUCTION_SET[KeyWords.CSLC]: CSLC,
        KeyWords.INSTRUCTION_SET[KeyWords.CSRC]: CSRC,
        KeyWords.INSTRUCTION_SET[KeyWords.CALL]: CALL,
        KeyWords.INSTRUCTION_SET[KeyWords.RET]: RET
    }
