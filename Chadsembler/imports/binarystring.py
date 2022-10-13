"""
Module containing the 'BinaryString' class
"""

class BinaryString:
    """
    -Class storing all functionality required to generate and read binary strings
    -Additional functionality such for the binary strings such as operations (like bitwise shifts) are also present in this class
    -All members and methods are static, the class is merely a namespace for all this functionality, logically grouping all the data together
    -Modularises the program by grouping all binary string related data into a single module, making it self-contained
    """

    @staticmethod
    def toBinary(denaryNumber: int) -> str:
        """Given a denary value, will return the string representation of the binary value"""

        # Python's built-in bin() function takes in an integer as an argument and returns the binary representation of the integer as a string
        # The binary is prefixed with 0b
        # For example bin(7) will return '0b111'
        # The '0b' part of the string will be sliced off and just the actual binary part of it will be returned from this static method
        # The method will only convert the magnitude of the denary number into binary
        # I can achieve this by taking the absolute value of the denaryNumber
        return bin(int(abs(denaryNumber)))[2:]

    @staticmethod
    def numberOfBits(denaryNumber: int) -> int:
        """Calculate the minimum number of bits a denary value would need to be represented as an integer"""

        # The number of bits can be calculated by getting the length of the binary string representation of the integer
        return len(BinaryString.toBinary(denaryNumber))

    @staticmethod
    def padBinary(binaryString: str, padNumber: int, padValue: str = '0'):
        """Left pad a binary number with either a '0' or a '1' a specified amount of times
            Important for ensuring binary is held in a fixed number of bits rather than only 
                the minimum amount of bits needed to represent an integer only being present"""

        
        # Prepend (left-pad) the binary string with the fixed number of bits
        return (padValue * padNumber) + binaryString 

    @staticmethod
    def unsignedInteger(denaryValue: int, numberOfBits: int) -> str:
        """Create an unsigned integer binary string for a given denary value"""

        # An unsigned integer, at most, must have at least one bit available
        if numberOfBits < 1:

                numberOfBits = 1

        # Generate the number to its binary string equivalent
        binaryAsString: str = BinaryString.toBinary(denaryValue % (2**numberOfBits))
        
        # Return the binary string, left padded with 0 to ensure a fixed number of bits
        return BinaryString.padBinary(binaryAsString, (numberOfBits - len(binaryAsString)), '0')  

    @staticmethod
    def signedInteger(denaryValue: int, numberOfBits: int) -> str:
        """Create a signed integer binary string for a given denary value"""

        # An unsigned integer, at most, must have at least two bit available
        # one for the sign bit and at least one to represent an actual value
        if numberOfBits < 2:

            numberOfBits = 2

        signBit: str = '0'  # The sign bit will default to '0' (begin by assuming the number is positive)

        if denaryValue < 0:  # Check to see whether the value is negative

            signBit = '1'  # If negative then update the sign bit to '1' - a sign bit of '1' means the value is negative

            # Get the absolute value of denary value
            # The binary string can be generated by generating the binary string for the 
            # magnitude of the integer and then prepending the sign bit to the binary string
            denaryValue = abs(denaryValue)

        binaryAsString: str = BinaryString.toBinary(denaryValue % (2**(numberOfBits-1)))  # Generate the binary string for the value

        # Pad the binary string with the the amount of bits left needed to reach the specified numberOfBits
        # 'len(binaryAsString) - 1' is used to account for the extra sign bit that'll be prepended to the left padded binary string
        # The sign bit is prepended to the binary string, resulting in the final signed integer that can then be returned to the caller
        return signBit + BinaryString.padBinary(binaryAsString, ((numberOfBits - len(binaryAsString) - 1)), '0')

    @staticmethod
    def readUnsignedInteger(unsignedInteger: str) -> int:
        """Given an unsigned binary string, evaluate it to a denary value"""

        # Python has a built in to-integer function with a definition of int(target, base)
        # The function can read unsigned binary strings and evaluate them to an integer
        # As long as we pass in '2' for the 'base' argument it will then interpret the passed in value as a base 2 value (binary)
        return int(unsignedInteger, 2)

    @staticmethod
    def readSignedInteger(signedInteger: str) -> int:
        """Given a signed binary string, evaluate it to a denary value"""

        # Determine the sign of the value from the sign bit
        # A sign bit of '0' connotes the value is positive
        # A sign bit of '1' (the only other case if it is not '0') connotes the value represented is negative
        sign = 1 if signedInteger[0] == '0' else -1

        # Python has a built in to-integer function with a definition of int(target, base)
        # The function can read unsigned binary strings and evaluate them to an integer
        # The value part of the signed integer will be passed in to the function so it may be evaluated to an integer
        # The value will then be multiplied by the sign so the positive-ness/negative-ness of the number is actually reflected in the final value
        # The value is then returned to the caller
        return sign * int(signedInteger[1:], 2)


    # ====================== Shift Instructions
    #   All shift instructions will perform the appropriate shift on a given binary string
    #   Each method responsible for performing a shift will return the carry bit (value shifted out of the binary) and the new value
    #   In short:   return carryBit, newValue
    #   The only exception to are the circular left shift and circular right shift - bits wrap around rather than being shifted into the carry bit

    #   LSB = Least Significant Bit (right-most bit)
    #   MSB = Most Significant Bit (left-most bit)

    @staticmethod
    def logicalShiftLeft(binaryString: str):
        """Perform a logical left shift on a given binary string"""

        # A logical left shift will move all values to the left
        # The MSB will be shifted out of the binary
        # The right side of the binary is padded with '0's to fill the empty space
        return binaryString[0], binaryString[1:] + '0'

    @staticmethod
    def logicalShiftRight(binaryString: str):
        """Perform a logical right shift on a given binary string"""

        # A logical right shift will move all values to the right
        # The LSB will be shifted out of the binary
        # The left side of the binary is padded with '0's to fill the empty space
        return binaryString[-1], '0' + binaryString[:-1]

    @staticmethod
    def arithmeticShiftLeft(binaryString: str):
        """Perform an arithmetic left shift on a given binary string"""

        # The bit after the MSB (second bit from the left) is shifted into the carry bit
        # All bits move a space to the left
        # It is then right-padded with the MSB to preserve the sign bit
        return binaryString[1], binaryString[1:] + binaryString[0]

    @staticmethod
    def arithmeticShiftRight(binaryString: str):
        """Perform an arithmetic right shift on a given binary string"""

        # The LSB is shifted into the carry bit
        # All bits move a space to the right
        # It is then left-padded with the MSB to preserve the sign bit
        return binaryString[-1], binaryString[0] + binaryString[:-1]

    @staticmethod
    def circularShiftLeft(binaryString: str):
        """Perform a circular left shift
            Different to a circular left shift with carry"""
        
        # Special-case shift instruction, no carry bit is leftover from the operation

        # The MSB wraps around and becomes the LSB
        return binaryString[1:] + binaryString[0]

    @staticmethod
    def circularShiftRight(binaryString: str):
        """Perform a circular right shift
        Different to a circular right shift with carry"""

        # Special-case shift instruction, no carry bit is leftover from the operation

        # The LSB wraps around and becomes the MSB
        return binaryString[-1] + binaryString[:-1]

    @staticmethod
    def circularShiftLeftWithCarry(binaryString: str, carryBit='0'):
        """Perform a circular left shift with the carry bit
        Different to a circular left shift"""

        # As the carry bit is used in this shift, it must be passed in as an argument to the method
        # While encouraged to pass in a value for the carry bit, 
        # if no value is passed in then a default carry bit of '0' will be assumed

        # The MSB is shifted into the carry bit
        # All bits move a space to the left
        # It is then right-padded with the old carry bit
        return binaryString[0], binaryString[1:] + carryBit[-1]

    @staticmethod
    def circularShiftRightWithCarry(binaryString: str, carryBit='0'):
        """Perform a circular right shift with the carry bit
        Different to a circular right shift with carry"""

        # As the carry bit is used in this shift, it must be passed in as an argument to the method
        # While encouraged to pass in a value for the carry bit, 
        # if no value is passed in then a default carry bit of '0' will be assumed

        # The LSB is shifted into the carry bit
        # All bits move a space to the right
        # It is then left-padded with the old carry bit
        return binaryString[-1], carryBit[-1] + binaryString[:-1]