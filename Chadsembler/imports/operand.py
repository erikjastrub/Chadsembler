"""
Module containing the 'Operand' class
"""

class Operand:
    """
    -Class grouping together attributes related to an instruction operand
    -Provides a logical way to group and access operand related data
    -Dataclass so all members are public as mutating them won't affect anything
    """

    # --Class Members / Object Attributes
    addressingMode: "TypedToken"
    operandValue: "TypedToken"

    # --Object Methods
    def __init__(self: "Operand", addressingMode: "TypedToken", operandValue: "TypedToken") -> None:
        """Constructor for an `Operand` object"""

        # The addressing mode of the operand
        self.addressingMode: "TypedToken" = addressingMode

        # The actual operand value, can either be a Register, Label or actual Value
        self.operandValue: "TypedToken" = operandValue  
