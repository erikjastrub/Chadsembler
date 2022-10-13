"""
Module containing the 'KeyWords' class
"""

class KeyWords:
    """
    -Class used as a namespace, grouping all keyword related data
    -Critical data for modules found all across the whole project can be found in this class
    -This is beneficial as it makes the program more modular
    -This also makes the program more memory efficient as data that can be shared between classes will be defined once in this class rather than multiple times between many classes
    """

    # Instruction Set - Instruction Format: INSTRUCTION SOURCE, DESTINATION
    
    HLT: str = "HLT"  # 0 operand - Suspend the execution of the program, End the program
    ADD: str = "ADD"  # 2 operand - ADD the value in the SOURCE operand onto the value in the DESTINATION operand
    SUB: str = "SUB"  # 2 operand - Subtract the value in the SOURCE operand from the value in the DESTINATION operand
    STA: str = "STA"  # 2 operand - Store the value held in the DESTINATION operand into the address at SOURCE
    NOP: str = "NOP"  # 0 operand - Perform no operation, exhaust 1 clock cycle
    LDA: str ="LDA"  # 2 operand - Load the value held in the SOURCE operand onto the address held in the DESTINATION operand 
    BRA: str = "BRA"  # 2 operand - Always branch to the branch label in the SOURCE operand regardless what value is in the DESTINATION operand
    BRZ: str = "BRZ"  # 2 operand - Branch if the value in the DESTINATION operand == 0 to the branch label in the SOURCE OPERAND
    BRP: str = "BRP"  # 2 operand - Branch if the value in the DESTINATION operand >= 0 to the branch label in the SOURCE OPERAND
    INP: str = "INP"  # 1 operand - Get input from stdin (the default input stream) and store it in the address in the first operand
    OUT: str = "OUT"  # 1 operand - Output the integer value held in the SOURCE operand
    OUTC: str = "OUTC"  # 1 operand - Output the value as a character (ascii encoded) held in the SOURCE operand
    OUTB: str = "OUTB"  # 1 operand - Output the binary (ascii encoded) held in the SOURCE operand
    AND: str = "AND"  # 2 operand - Perform a bitwise AND on the DESTINATION operand with a mask of the source operand
    OR: str = "OR"  # 2 operand - Perform a bitwise OR on the DESTINATION operand with a mask of the SOURCE operand
    NOT: str = "NOT"  # 2 operand - Invert all the bits in the SOURCE operand and store it in the DESTINATION operand
    XOR: str = "XOR"  # 2 operand - Perform a bitwise XOR on the DESTINATION operand with a mask of the SOURCE operand
    LSL: str = "LSL"  # 2 operand - Perform a logical shift left on the DESTINATION operand by the value held in the SOURCE operand
    LSR: str = "LSR"  # 2 operand - Perform a logical shift right on the DESTINATION operand by the value held in the SOURCE operand
    ASL: str = "ASL"  # 2 operand - Perform an arithmetic shift left on the DESTINATION operand by the value held in the SOURCE operand
    ASR: str = "ASR"  # 2 operand - Perform an arithmetic shift right on the DESTINATION operand by the value held in the SOURCE operand
    CSL: str = "CSL"  # 2 operand - Perform a circular shift left on the DESTINATION operand by the value held in the SOURCE operand
    CSR: str = "CSR"  # 2 operand - Perform a circular shift right on the DESTINATION operand by the value held in the SOURCE operand
    CSLC: str = "CSLC"  # 2 operand - Perform a circular shift left with carry on the DESTINATION operand by the value held in the SOURCE operand
    CSRC: str = "CSRC"  # 2 operand - Perform a circular shift right with carry on the DESTINATION operand by the value held in the SOURCE operand
    CALL: str = "CALL"  # 1 operand - CALL the procedure held in the first operand, will store the instruction pointer onto the return register so the procedure may be RETurned from
    RET: str = "RET"  # 0 operand - Set the Instruction Pointer to the value held in the Return Register to continue program execution from that point

    INSTRUCTION_SET: dict[str, int] = {  # Dictionary mapping the instructions to opcode
        HLT: 0,
        ADD: 1,
        SUB: 2,
        STA: 3,
        NOP: 4,
        LDA: 5,
        BRA: 6,
        BRZ: 7,
        BRP: 8,
        INP: 9,
        OUT: 10,
        OUTC: 11,
        OUTB: 12,
        AND: 13,
        OR: 14,
        NOT: 15,
        XOR: 16,
        LSL: 17,
        LSR: 18,
        ASL: 19,
        ASR: 20,
        CSL: 21,
        CSR: 22,
        CSLC: 23,
        CSRC: 24,
        CALL: 25,
        RET: 26
    }

    # Inverse of the instruction set dictionary, mapping opcodes to instructions
    OPCODE_TO_INSTRUCTION: dict[int, str] = { value: key for key, value in INSTRUCTION_SET.items() }  

    # Cache the number of instructions into a static member of the class to avoid having to recompute it
    NUMBER_OF_INSTRUCTIONS: int = len(INSTRUCTION_SET)

    # Instruction Related Data

    # Map the instruction to how many operands it operates on at most
    NUMBER_OF_INSTRUCTION_OPERANDS: dict[str, int] = {
        HLT: 0,
        NOP: 0,
        RET: 0,

        INP: 1,
        OUT: 1,
        OUTC: 1,
        OUTB: 1,
        CALL: 1,
        

        ADD: 2,
        SUB: 2,
        STA: 2,
        LDA: 2,
        BRA: 2,
        BRZ: 2,
        BRP: 2,
        AND: 2,
        OR: 2,
        NOT: 2,
        XOR: 2,
        LSL: 2,
        LSR: 2,
        ASL: 2,
        ASR: 2,
        CSL: 2,
        CSR: 2,
        CSLC: 2,
        CSRC: 2
    }

    # Instructions responsible for transferring data, the source operand cannot be in immediate mode
    DATA_FLOW_INSTRUCTIONS: tuple[str] = (  
        STA, INP
    )

    # Single operand instructions that must have the operand present, other single operand instructions can have their operand inferred
    EXPLICIT_SINGLE_OPERAND_INSTRUCTIONS: tuple[str] = (  
        CALL,
    )

    # Program Counter manipulating instructions, able to manipulate the flow of a program and help implement logic
    BRANCH_INSTRUCTIONS: tuple[str] = (  
        BRA,
        BRZ,
        BRP
    )

    # Program Counter manipulating instructions that are used to call procedures
    CALL_INSTRUCTIONS: tuple[str] = (  
        CALL,
    )

    # Special type of data transfer instruction, gathering external input
    INPUT_INSTRUCTIONS: tuple[str] = (  
        INP,
    )

    # Assembly Directives

    # Used to declare variables which map to a memory address under the hood
    DAT: str = "DAT"  

    # A dictionary mapping an assembly directive to its underlying integer equivalent
    ASSEMBLY_DIRECTIVES: dict[str, int] = {  
        DAT: 0
    }

    # Addressing Modes

    IMMEDIATE_ADDRESSING_MODE: str = '#'  # The operand is the actual value
    DIRECT_ADDRESSING_MODE: str = '@'  # The operand is the address storing the value
    INDIRECT_ADDRESSING_MODE: str = '>'  # The operand is an address holding the address of the value (2 layers of direct addressing)
    REGISTER_ADDRESSING_MODE: str = '%'  # The operand is the value in a register

    # All addressing mode characters grouped together
    ADDRESSING_MODE_CHARACTERS: str = IMMEDIATE_ADDRESSING_MODE + DIRECT_ADDRESSING_MODE + \
                                INDIRECT_ADDRESSING_MODE + REGISTER_ADDRESSING_MODE  

    # Cache the number of addressing modes into a static member of the class to avoid having to recompute it
    NUMBER_OF_ADDRESSING_MODES: int = len(ADDRESSING_MODE_CHARACTERS)

    # A dictionary mapping all addressing modes into its symbol equivalent, this allows for multiple identifiers to refer to the same addressing mode
    ADDRESSING_MODES: dict[str, str] = {
        "IMMEDIATE": IMMEDIATE_ADDRESSING_MODE,
        "DIRECT": DIRECT_ADDRESSING_MODE,
        "INDIRECT": INDIRECT_ADDRESSING_MODE,
        "REGISTER": REGISTER_ADDRESSING_MODE,
        IMMEDIATE_ADDRESSING_MODE: IMMEDIATE_ADDRESSING_MODE,
        DIRECT_ADDRESSING_MODE: DIRECT_ADDRESSING_MODE,
        INDIRECT_ADDRESSING_MODE: INDIRECT_ADDRESSING_MODE,
        REGISTER_ADDRESSING_MODE: REGISTER_ADDRESSING_MODE,
    }

    ADDRESSING_MODE_TO_OPCODE: dict[str, int] = {  # A dictionary mapping an addressing mode to its opcode
        REGISTER_ADDRESSING_MODE: 0,
        INDIRECT_ADDRESSING_MODE: 1,
        DIRECT_ADDRESSING_MODE: 2,
        IMMEDIATE_ADDRESSING_MODE: 3
    }

    # Registers

    # A dictionary mapping all general purpose register identifiers into one single identifier, 
    #   this allows for multiple identifiers to refer to a general purpose register

    GENERAL_PURPOSE_REGISTER: dict[str, str] = {
        "REGISTER": "REG",
        "REG": "REG",
        "R": "REG"
    }

    ACCUMULATOR: str = "ACC"  # The accumulator, used as the default register for operations
    RETURN_REGISTER: str = "RR"  # Stores the return address of a procedure - the address to return to when RETturning from a procedure
    FLAGS_REGISTER: str = "FR"  # Stores any excess operation data such as carry bits from shift instructions
    PROGRAM_COUNTER: str = "PC" # Stores the address of the current instruction being executed

    # Store all special-purpose register related keywords
    SPECIAL_PURPOSE_REGISTERS: dict[str, str] = {
        "ACCUMULATOR": ACCUMULATOR,
        ACCUMULATOR: ACCUMULATOR,
        "RETURNREGISTER": RETURN_REGISTER,
        RETURN_REGISTER: RETURN_REGISTER,
        "FLAGSREGISTER": FLAGS_REGISTER,
        FLAGS_REGISTER: FLAGS_REGISTER,
        "PROGRAMCOUNTER": PROGRAM_COUNTER,
        PROGRAM_COUNTER: PROGRAM_COUNTER
    }

    # The offset for each special purpose register, extremely important for code generation
    SPECIAL_PURPOSE_REGISTERS_OFFSET: dict[str, int] = {  

        # Each register has an underlying address associated with it to access it
        # General purpose registers have an address that matches their number
        # For example REG1 will be accessed with sn address of '1', REG2 will be accessed with an address of '2', etc.
        # This is a more natural and logical fit for when accessing general purpose registers, 
        #   it also makes it easier to read a chadsembly machine code instruction
        # The special purpose registers will have an address beginning from the end of the general purpose register addresses
        # For example, if there are 3 general purpose registers, then the first special purpose register (the ACCUMULATOR) will be found at address 4
        # This mapping allows for the addresses of the special purpose registers to be calculated and then accessed
        # The formula for the address of a special purpose register is: Number Of General Purpose Registers + Special Purpose Register Offset
        # For example, to access the ACCUMULATOR using this mapping, the instruction will look like this:
        #       addressOfAccumulator = KeyWords.SPECIAL_PURPOSE_REGISTERS_OFFSET[KeyWords.ACCUMULATOR] + numberOfGeneralPurposeRegisters

        # The offset begins from 1 and not 0, an offset of 0 would mean 
        #   one of the addresses for a special purpose register will overlap with one of a general purpose register
        ACCUMULATOR: 1,
        PROGRAM_COUNTER: 2,
        RETURN_REGISTER: 3,
        FLAGS_REGISTER: 4,
    }

    # Cache the number of special purpose registers into a static member of the class to avoid having to recompute it
    NUMBER_OF_SPECIAL_PURPOSE_REGISTERS: int = len(SPECIAL_PURPOSE_REGISTERS_OFFSET)  

    # Instruction Separator

    OPERAND_SEPERATOR_CHARACTERS: str = ","  # The characters connoting the separation of instruction operands

    # Block Scope

    BLOCK_SCOPE_CHARACTERS: str = "{}"  # All block scope related characters
    LEFT_SCOPE_CHARACTERS: str = "{"  # Scope opening characters
    RIGHT_SCOPE_CHARACTERS: str = "}"  # Scope closing characters

    # Code Formatting - important for the lexer

    WHITE_SPACE_CHARACTERS: str = " \t\v"  # White space characters, should be skipped over
    LINE_BREAK_CHARACTERS: str = "\n\r\f"  # Beginning of a new line / end of the current line

    BEGINNING_OF_LABEL_CHARACTERS: str = "abcdefghijklmnopqrstuvwxyz" "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "_"  # Characters a label may begin with
    LABEL_CHARACTERS: str = "abcdefghijklmnopqrstuvwxyz" "ABCDEFGHIJKLMNOPQRSTUVWXYZ" "_" "1234567890"  # Characters a label can only consist of

    VALUE_CHARACTERS: str = "1234567890"  # Characters a value (integer) can only consist of
    VALUE_SIGNS: str = "+-"  # Characters connoting the sign (positive or negative) of a value
    BEGINNING_OF_VALUE_CHARACTERS: str = "+-" "1234567890"  # Characters a value may begin with
