"""
Module containing the 'TypedToken' class that inherits from the 'Position' class
"""

from position import Position

class UntypedToken(Position):
    """
    -Encapsulates all token related data
    -As tokens also store positional related data it is suitable to inherit from the `Position` class
    -Data class, storing related token data together
    -As it is a dataclass, all members are public as mutating the state of any of the members won't affect the inner-workings of the class
    -Keeping members public also avoid the unnecessary computation that come with getters and setters 
        such as an extra function call to mutate an attribute when no validation or processing needs to be done
    """

    # --Class Members / Object Attributes
    tokenValue: str
    # --Inherited Class Members / Object Attributes
    row: int
    column: int


    # --Object Methods
    def __init__(self: "UntypedToken", tokenValue: str, row: int, column: int) -> None:
        """Constructor for an `UntypedToken` object"""

        Position.__init__(self, row, column)  # Call super class' constructor to initialise inherited attributes
        self.tokenValue = tokenValue  # a string representation of the value being stored by the token
