"""
Module containing the 'VirtualMachine' class
"""

import sys
from binarystring import BinaryString
from defaults import Defaults
from keywords import KeyWords
from machineoperations import MachineOperations
import time
from colour import Colour

class VirtualMachine:
    """
    -Class encapsulating all functionality needed to execute chadsembly byte code
    -The VM is responsible for creating the memory pool as well as addressable space for the general and special purpose registers
    -Memory safety and operation execution are both closely guarded by the VM
    -The VM is also responsible for ensuring the correct values for both the source operand and destination operand generated
    """

    # --Class Members / Object Attributes
    configurationTable: dict[str, int]
    chadsemblyByteCode: list[str]
    numberOfMachineOperationBits: int
    numberOfAddressingModeBits: int
    numberOfOperandBits: int
    totalNumberOfInstructionBits: int
    memoryPool: list[str]
    machineOperations: MachineOperations

    # --Object Methods
    def __init__(self: "VirtualMachine", configurationTable: dict[str, int], chadsemblyByteCode: list[str],
                 numberOfMachineOperationBits: int, numberOfAddressingModeBits: int, numberOfOperandBits: int, totalNumberOfInstructionBits: int) -> None:
        """Constructor for a `VirtualMachine` object"""

        # The configuration table storing the VM configuration options (the parameters the VM can be fine-tuned to)
        # Important values such as the number of memory addresses or number of general purpose registers are stored in the configuration table
        self.__configurationTable: dict[str, int] = configurationTable

        # The actual chadsembly byte code (resemblant of machine code) that the VM needs to execute
        # In this pool of bytecode there are also the variables that have been initialised with their requested values (or default value)
        self.__chadsemblyByteCode: list[str] = chadsemblyByteCode

        self.__numberOfMachineOperationBits: int = numberOfMachineOperationBits  # The number of bits the machine operation part of the opcode consists of
        self.__numberOfAddressingModeBits: int = numberOfAddressingModeBits  # The number of bits the addressing mode part of the opcode consists of 
        self.__numberOfOperandBits: int = numberOfOperandBits  # The number of bits an operand consists of
        self.__totalNumberOfInstructionBits: int = totalNumberOfInstructionBits  # The number of bits an entire chadsembly instruction consists of

        # The memory pool that chadsembly instructions should be able to manipulate
        # The memory pool will map an address to an actual memory location or general/special purpose register
        # All memory addresses are accessed through a corresponding positive value - E.g. Memory Address 1 will be accessed through the key 1, Address 2 will be accessed through the key 2, etc.
        # All special/general purpose registers are accessed through the negative version of the corresponding number - E.g. General Purpose Register 1 will be accessed through the key -1, etc.
        # This is to ensure they both can be accessed through the same memory pool but dont overlap (E.g. memory location 1 doesn't overlap with general purposes register 1)
        # This approach saves computation and is more efficient than if there were a separate address pool for both memory locations and registers
        # It is more efficient as it avoids the need to perform additional validation checks to determine between memory location and register
        # Under the hood the corresponding address just needs to be calculated and then it can be accessed through this dictionary in constant time
        # A dictionary has been used instead of a conventional array or list
        # This is because you cannot access negative indexes in an array and the address of registers are represented by a corresponding negative value under the hood
        # A dictionary can still be manipulated in an array-like manner as accessing a value from a key is resemblant of accessing a value from an index
        # array[0] is resemblant of dictionary[0]
        self.__memoryPool: dict[int, str] = self.__generateMemoryPool()

        # An instance of the 'MachineOperations' class is instantiated and used as an attribute
        # This obviously will store the actual machine operations that can be performed by the VM
        # The machine operations will have access to the same memory pool so it may be manipulated
        # The machine operations will also store a dictionary mapping an opcode to its corresponding machine operations, greatly boosting performance
        # This mapping boosts performance as it avoids the need to write a selection statement for each machine operation
        self.__machineOperations: MachineOperations = MachineOperations(self.__memoryPool, self.__totalNumberOfInstructionBits, configurationTable[Defaults.REGISTERS_CONFIGURATION_OPTION])

    def __generateMemoryPool(self: "VirtualMachine") -> dict[int, str]:
        """Create the instruction pool using the configuration table and initialise each memory location and register with a default value"""

        # Generate the total value, ensure it is in a fixed number of bits - the same number of bits as the address bus or total number of bits for an instruction
        # It is important it is the same number of bits as an instruction (same width) to ensure each address stores a uniform amount of bits
        # The way a CPU works is it fetches what it presumes to be an instruction and then attempts to decode and execute it
        # It will decode it to, grabbing the set amount of bits for the machine operation, addressing mode and operands
        # It will then try to determine what machine operation it is, what data needs to be accessed, etc.
        # A CPU has no way to tell if the bits held at an address are for an instruction or value
        # If the Program Counter points to it then it will fetch it and attempt to decode and execute it
        # This is exactly why it is critical a programmer /compiler ensures the CPU only ever works over actual instructions in memory
        # If a CPU attempts to FDE a value it may result in undefined behaviour (for example the value may by sheer chance be the value for an instruction) or it may result in the CPU breaking in some way
        # FUN FACT: Some CPUs have a "Safe Mode" which is at the actual driver level which attempts to ensure that it only executes what it knows or can determine to be instructions
        defaultValue: str = '0' * self.__totalNumberOfInstructionBits

        # The number of addresses can be calculated from the number of operand bits
        # As an operand must be able to address all addresses, the maximum value that can be represented from the bits of an operand can be used to determine how many memory locations there are
        # If a user requests for 100 memory addresses, 100 in binary is '1100100' which is 7 bits long
        # A binary number consisting of 7 bits can represent a maximum value of ((2**7) - 1) which equals to 127
        # Rather than creating a memory pool of only 100 addresses, as at most 127 can be represented, a memory pool of 127 memory locations will be created
        # This is obviously to ensure that if an operand can address it, it can be accessible, it also makes the most of the number of bits available
        # The Memory configuration option should be thought of as requesting the minimum amount of addresses you'd like
        numberOfMemoryAddresses: int = 2 ** (self.__numberOfOperandBits - 1)

        # Update the configuration table to store the actual amount of memory locations
        self.__configurationTable[Defaults.MEMORY_CONFIGURATION_OPTION] = numberOfMemoryAddresses

        # The number of registers (both special and general purpose)
        totalNumberOfRegisters: int = self.__configurationTable[Defaults.REGISTERS_CONFIGURATION_OPTION] + KeyWords.NUMBER_OF_SPECIAL_PURPOSE_REGISTERS

        # Generate the memory pool, initialising each location with the default value
        # The memory pool will be a dictionary mapping a location to the value at the location
        # It will be manipulated in a array-like manner as the keys can be treated as if they were array indexes (with keys being integers)
        # A dictionary comprehension is used to generate a dictionary containing keys '0 to numberOfMemoryAddresses' all initialised to the default value
        memoryPool: dict[int, str] = { index: defaultValue for index in range(numberOfMemoryAddresses)}

        # Initialise the addresses that are used for the special and general purpose registers to the default value
        for register in range(totalNumberOfRegisters, 0, -1):

            memoryPool[register*-1] = defaultValue  # A register is represented by the negative version of the corresponding register number which is why the register control variable is multiplied by -1

        return memoryPool  # Return the generated and initialised memory pool to the caller

    def __loader(self: "VirtualMachine") -> None:
        """Load the chadsembly byte code into the memory pool, validating that it can be loaded into memory in its entirety"""

        numberOfChadsemblyInstructions: int = len(self.__chadsemblyByteCode)  # Cache the number of instructions in a variable to avoid having to recompute it
        numberOfMemoryLocations: int = self.__configurationTable[Defaults.MEMORY_CONFIGURATION_OPTION]  # Cache the number of memory locations in a variable to avoid having to recompute it

        if numberOfChadsemblyInstructions > numberOfMemoryLocations:  # If there are more instructions than there are memory locations

            # Output an error message in red and suspend the program
            sys.exit(f"{Colour.RED}Runtime Error: Cannot load all instructions and any variables into memory - {numberOfChadsemblyInstructions} instructions cannot fit into a memory pool of {numberOfMemoryLocations} locations{Colour.RESET}")

            # Don't need to return as sys.exit() will end the program meaning the rest of the function won't be reached

        for index in range(len(self.__chadsemblyByteCode)):  # Count controlled loop

            # Load the chadsembly byte code into memory chronologically
            # For example: The byte code at address 0 will be loaded into memory address 0
            self.__memoryPool[index] = self.__chadsemblyByteCode[index]

    def __generateIntroductionPrompt(self: "VirtualMachine") -> str:
        """Will generate the python interactive-mode inspired introduction prompt, outlining important details of the current run-time like the number of bits used for an instruction or the maximum range of accessible values"""

        maximumValueInOperand: int = 2 ** (self.__numberOfOperandBits - 1) - 1  # Calculate the maximum value that can be stored in an operand
        maximumValueInMemoryLocation: int = 2 ** (self.__totalNumberOfInstructionBits - 1) - 1  # Calculate the maximum value that can be stored in a memory location

        # Generate the way an instruction looks and what bits correspond to what in the instruction
        instructionFormat: str = f"{'0'*self.__numberOfMachineOperationBits} {'0'*self.__numberOfAddressingModeBits} {'0'*self.__numberOfOperandBits} {'0'*self.__numberOfOperandBits}"

        numberOfAddresses: int = 2 ** (self.__numberOfOperandBits - 1)  # Calculate how many memory locations can be accessed
        numberOfGeneralPurposeRegisters: int = self.__configurationTable[Defaults.REGISTERS_CONFIGURATION_OPTION]  # Calculate how many general purpose registers can be accessed

        # Generate the introduction prompt and return it to the caller
        return f"""Chadsembly Version 6.15b - {self.__numberOfOperandBits} bit operand - {self.__totalNumberOfInstructionBits} bit address bus - Instruction Format: {instructionFormat}
Values in the range -{maximumValueInOperand} ... {maximumValueInOperand} are addressable in an operand, Values in the range -{maximumValueInMemoryLocation} ... {maximumValueInMemoryLocation} may be stored in a memory address
{numberOfAddresses} (0...{numberOfAddresses-1}) memory addresses and {numberOfGeneralPurposeRegisters} (1...{numberOfGeneralPurposeRegisters}) general purpose registers are available for use\n"""

    def __resolveForValue(self: "VirtualMachine", addressingMode: int, operandValue: int) -> int:
        """Resolve the operand to the value it stores or is pointing to
           Used to resolve source operands for non-data transfer instructions like ADD, SUB, LSL, etc."""

        if addressingMode == KeyWords.ADDRESSING_MODE_TO_OPCODE[KeyWords.DIRECT_ADDRESSING_MODE]:  # If the addressing mode is Direct Addressing Mode

            # The value is stored at the address in the operand
            return BinaryString.readSignedInteger(self.__memoryPool[operandValue])

        elif addressingMode == KeyWords.ADDRESSING_MODE_TO_OPCODE[KeyWords.INDIRECT_ADDRESSING_MODE]:  # If the addressing mode is Indirect Addressing Mode

            # The operand is storing the address of the address storing the value
            # This is essentially 2 layers of direct mode
            return  BinaryString.readSignedInteger(self.__memoryPool[BinaryString.readSignedInteger(self.__memoryPool[operandValue])])

        elif addressingMode == KeyWords.ADDRESSING_MODE_TO_OPCODE[KeyWords.REGISTER_ADDRESSING_MODE]:  # If the addressing mode is Register Addressing Mode

            # The value is in a register
            return BinaryString.readSignedInteger(self.__memoryPool[operandValue * -1])

        elif addressingMode ==  KeyWords.ADDRESSING_MODE_TO_OPCODE[KeyWords.IMMEDIATE_ADDRESSING_MODE]:  # If the addressing mode is Immediate Addressing Mode

            # The operand is the actual value
            return  operandValue

    def __resolveForAddress(self: "VirtualMachine", addressingMode: int, operandValue: int) -> int:
        """Resolve the operand to the direct address of the value it is pointing to
           Used to resolve source operands data transfer instructions like STA, INP, etc."""

        if addressingMode == KeyWords.ADDRESSING_MODE_TO_OPCODE[KeyWords.INDIRECT_ADDRESSING_MODE]:  # If the addressing mode is Indirect Addressing Mode

            # The operand is storing the address of the address storing the value
            # This means to resolve it for an address we need the address the source operand is holding
            return BinaryString.readSignedInteger(self.__memoryPool[operandValue])

        elif addressingMode ==  KeyWords.ADDRESSING_MODE_TO_OPCODE[KeyWords.REGISTER_ADDRESSING_MODE]:

            # Generate the underlying address used to access a register
            # Under the hood, registers are represented by the negative version of the corresponding address number
            # And so to resolve for an address we'll simply return the value * -1 to turn it negative
            return operandValue * -1

        # Default case covering immediate and direct addressing mode
        # The semantic analyser will ensure that any data transfer instruction's source operand isn't in immediate mode
        # However this will still cover the case in which the addressing mode is in immediate addressing mode
        # When resolving an immediate addressing mode for an address, it will resolve the same value as if an operand in direct mode was being resolved for an address
        # For example: IMMEDIATE 5 is resolved to address 5 and DIRECT 5 is also resolved to address 5
        return operandValue

    def __resolveForBinary(self: "VirtualMachine", addressingMode: int, operandValue: int) -> str:
        """Resolve the operand to get the binary for it
           Used for special instructions that operate on the pure binary (E.g. OUTB)"""

        if addressingMode == KeyWords.ADDRESSING_MODE_TO_OPCODE[KeyWords.DIRECT_ADDRESSING_MODE]:  # If the addressing mode is Direct Addressing Mode

            # The binary is stored at the address in the operand
            return self.__memoryPool[operandValue]

        elif addressingMode == KeyWords.ADDRESSING_MODE_TO_OPCODE[KeyWords.INDIRECT_ADDRESSING_MODE]:  # If the addressing mode is Indirect Addressing Mode

            # The operand is storing the address of the address storing the binary
            # This is essentially 2 layers of direct mode
            return  self.__memoryPool[BinaryString.readSignedInteger(self.__memoryPool[operandValue])]

        elif addressingMode == KeyWords.ADDRESSING_MODE_TO_OPCODE[KeyWords.REGISTER_ADDRESSING_MODE]:  # If the addressing mode is Register Addressing Mode

            # The value is in a register
            return self.__memoryPool[operandValue * -1]

        elif addressingMode ==  KeyWords.ADDRESSING_MODE_TO_OPCODE[KeyWords.IMMEDIATE_ADDRESSING_MODE]:  # If the addressing mode is Immediate Addressing Mode

            # Regenerate the binary for the operand in the case where it is in immediate mode
            return  BinaryString.signedInteger(operandValue, self.__totalNumberOfInstructionBits)

    def __inContainers(self: "VirtualMachine", targetValue: str, *containers: tuple[list]) -> bool:
        """Subroutine/helper function making it easier to read and perform the operation of checking for a value in multiple containers (lists, arrays, etc.)"""
        # *containers is the python syntax for a variable length of function arguments
        # The first argument to the method will always be the target value, but any subsequent arguments will get placed into a tuple called "containers"

        for container in containers:  # Iterate through each container

            if targetValue in container:  # If the target value is in the container

                return True  # Return True to signal it was found and is in one of the containers

        # If this point of the subroutine was reached then it is implied that the value was never found as if it was found then the function would have been exited early, with true being returned
        # And so we will return False to signal it is not in any of the containers
        return False

    def __resolveSourceOperand(self: "VirtualMachine", machineOperation: int, addressingMode: int, sourceOperand: int) -> int:
        """Given an operand, will determine whether it needs to be resolved for an address or value depending on the machine operation
           Meets the criteria that the VM ensures the correct source and destination operands are supplied to a machine operation"""

        # Attempt to get the instruction the opcode maps to...
        try:
            
            chadsemblyInstruction: str = KeyWords.OPCODE_TO_INSTRUCTION[machineOperation]

        except KeyError:

            # This error can only occur if the VM attempts to interpret a non-instruction as if it were an instruction
            # This happens if the programmer lets the PC point to a part of memory that doesn't contain an instruction
            # E.g. The programmer did not HLT the program and the PC overflowed into the variables stored in memory
            sys.exit(f"{Colour.RED}Runtime Error: The opcode {machineOperation} does not map to any machine operation\nThe Program Counter pointed to a non-instruction?{Colour.RESET}")

        if self.__inContainers(chadsemblyInstruction, KeyWords.DATA_FLOW_INSTRUCTIONS, KeyWords.BRANCH_INSTRUCTIONS, KeyWords.CALL_INSTRUCTIONS):
            # If the machine operation is found in any sort of data transfer instruction or any instruction who's source operand needs to be an address

            return self.__resolveForAddress(addressingMode, sourceOperand)  # Resolve the operand to an address and return it to the caller

        elif chadsemblyInstruction == KeyWords.OUTB:
            # If the instruction is the OUTB instruction, maintain the binary and return it to the caller
            return self.__resolveForBinary(addressingMode, sourceOperand)

        else:
            # If not then it is implied it must be resolved to a value

            return self.__resolveForValue(addressingMode, sourceOperand)  # Resolve the operand to a value and return it to the caller  
            

    def __resolveDestinationOperand(self: "VirtualMachine", destinationOperand: int) -> int:
        """A destination operand will always store the address of a register
           Given the destination operand, the underlying VM memory pool address for the register will be calculated and returned"""

        return destinationOperand * -1

    def __executeMachineOperation(self: "VirtualMachine", machineOperation: int, sourceOperand: int, destinationOperand: int) -> None:
        """Given a machine operation and its appropriate source and destination operands, perform the actual machine operation"""
        # A precondition to this method is that the source and destination operands have been resolved for their values and underlying addresses to access the data

        # Here the static dictionary mapping opcode to their machine code operation found in the MachineOperations class is made use of
        # If this mapping didn't exist then a massive selection statement (switch - case / if - else if) would be present in this method
        # The massive selection statement would slow the code down as each condition will need to be checked (making it an 0(n) operation in linear time)
        # The use of the mapping boosts performing as it makes the operation of getting the machine operation an O(1) constant time operation

        # As the mapping is a static member, after getting the machine operation and calling it, 
        #   we will need to pass in the actual machine operation instance as an argument so it knows what instance to operate on
        MachineOperations.instructionMapping[machineOperation](self.__machineOperations, sourceOperand, destinationOperand)

    def __executeInstruction(self: "VirtualMachine", chadsemblyInstruction: str) -> None:
        """Given a chadsembly bytecode instruction, break it down into its individual components and then call the necessary functionality to execute the machine operation
           This is resemblant of the Current Instruction Register - CIR which breaks down an instruction into its individual components - Opcode and Operand(s)"""

        # Calculate the underlying address for the special-purpose Program Counter register
        programCounterAddress: int = (self.__configurationTable[Defaults.REGISTERS_CONFIGURATION_OPTION] + KeyWords.SPECIAL_PURPOSE_REGISTERS_OFFSET[KeyWords.PROGRAM_COUNTER]) * -1

        # Increment the Program Counter to store the address of the next instruction
        self.__memoryPool[programCounterAddress] = BinaryString.signedInteger(BinaryString.readSignedInteger(self.__memoryPool[programCounterAddress]) + 1, self.__totalNumberOfInstructionBits)

        # The current offset is used as the upper limit to stop grabbing the substring from
        # A chadsembly code is stored as a string
        # To grab each part of the code (machine operation, addressing mode, operands) we will grab the substring of it in the string
        # The current offset will become the lower limit of the substring in subsequent substring grabbing operations but begin as the upper limit in the first substring grabbing operation
        # Substrings will be grabbed sequentially, allowing for this use of the currentOffset variable to be possible
        currentOffset: int = self.__numberOfMachineOperationBits

        # The machine operation is the bits beginning from index 0 to the currentOffset (which at this point is storing the number of machine operation bits)
        # The current offset will now be used as the upper limit to grab substrings from and is storing the beginning of the next part in the instruction: the addressing mode
        machineOperation: int = BinaryString.readUnsignedInteger(chadsemblyInstruction[0 : currentOffset])

        # The addressing mode can be grabbed beginning from the current offset to the (current offset + the number of addressing mode bits)
        # The current offset is updated to store this new value so it may now store the beginning of the next part in the instruction: the source operand
        addressingMode: int = BinaryString.readUnsignedInteger(chadsemblyInstruction[currentOffset : (currentOffset := currentOffset + self.__numberOfAddressingModeBits)])

        # The source operand can be grabbed beginning from the current offset to the (current offset + the number of operand bits)
        # The current offset is updated to store this new value so it may now store the beginning of the next part in the instruction: the destination operand
        sourceOperand: int = BinaryString.readSignedInteger(chadsemblyInstruction[currentOffset : (currentOffset := currentOffset + self.__numberOfOperandBits)])

        # The destination can be grabbed beginning from the current offset to the (current offset + the number of operand bits)
        # All parts of the instruction have now been grabbed
        destinationOperand: int = BinaryString.readSignedInteger(chadsemblyInstruction[currentOffset : (currentOffset := currentOffset + self.__numberOfOperandBits)])

        # Resolve the source operand to a value that can be used to when executing the actual machine operation
        sourceOperand = self.__resolveSourceOperand(machineOperation, addressingMode, sourceOperand)

        # Resolve the destination operand to the underlying memory pool address that can be used to when executing the actual machine operation
        destinationOperand = self.__resolveDestinationOperand(destinationOperand)

        # Now that the preconditions to execute the machine operation have been met (both operands have been resolved), we can now actually perform the machine operation
        self.__executeMachineOperation(machineOperation, sourceOperand, destinationOperand)

    def run(self: "VirtualMachine") -> None:
        """Wrapper method, binding all other methods to execute chadsembly bytecode in a memory-safe manner
        Should be treated as the main method of the preprocessor class, other methods should not be called individually"""

        self.__loader()  # First load the chadsembly bytecode into the memory pool

        # Output the introduction prompt to the terminal, this is resemblant of python's interactive shell introduction prompt
        print(f"{Colour.CYAN}{self.__generateIntroductionPrompt()}{Colour.RESET}")

        # Calculate the underlying address for the special-purpose Program Counter register and cache it in a variable so it doesn't need to be recalculated on each iteration of the loop
        programCounterAddress: int = (self.__configurationTable[Defaults.REGISTERS_CONFIGURATION_OPTION] + KeyWords.SPECIAL_PURPOSE_REGISTERS_OFFSET[KeyWords.PROGRAM_COUNTER]) * -1

        # Calculate the number of memory locations and cache it in a variable so it doesn't need to be recalculated on each iteration of the loop
        numberOfMemoryAddresses: int = self.__configurationTable[Defaults.MEMORY_CONFIGURATION_OPTION]

        # Calculate the clock speed (delay between the execution of each instruction) from milliseconds to seconds
        clockSpeed: float = self.__configurationTable[Defaults.CLOCK_CONFIGURATION_OPTION] / 1000

        while BinaryString.readSignedInteger(self.__memoryPool[programCounterAddress]) < numberOfMemoryAddresses:  # While in the memory-safe indexable bounds of the memory pool

            # Get the address stored in the Program Counter and generate the denary value for it
            # An instruction is an unsigned integer as it is not representing any sort of value, 
            #   it is merely stringing the combination of bits together into one binary string of bits
            # For example the instruction 00000000000000000000000 isn't meant to represent any sort of value, 
            #   but really is just the machine operation, addressing mode and operands joined together into 1 binary string of bits
            # This is so it may be transferred down the address bus in one go (match the same width as the address bus) rather than transferring each part individually: 000 0000 00000000 00000000
            programCounter: int = BinaryString.readUnsignedInteger(self.__memoryPool[programCounterAddress])

            time.sleep(clockSpeed)  # Delay the execution of the next instruction for the configured amount of time

            self.__executeInstruction(self.__memoryPool[programCounter])  # Execute the instruction
