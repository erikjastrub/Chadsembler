"""
Module containing the 'Position' class
"""

from keywords import KeyWords

class Position:
    """
    -Encapsulate all positional related data
    -Data class, storing related positional data together
    -As it is a dataclass, all members are public as mutating the state of any of the members 
        won't affect the inner-workings of the class
    -Keeping members public also avoid the unnecessary computation that come with getters and setters 
        such as an extra function call to mutate an attribute when no validation or processing needs to be done
    """

    # --Class Members / Object Attributes
    row: int
    column: int

    # --Object Methods
    def __init__(self: "Position", row: int, column: int) -> None:
        """Constructor for a `Position` object"""

        self.row: int = row  # A row can represent the line number in a text file, the current item in a list, etc.
        self.column: int = column  # A column can represent the current position in a line, current position in an item in a list, etc.

    def advancePosition(self: "Position", currentCharacter: str, resetValue: int = 1) -> None:
        """Given a character, update the row and column attributes accordingly,
            resetting the column attribute to the resetValue argument if a line-break character is found"""

        if currentCharacter in KeyWords.LINE_BREAK_CHARACTERS:  # if a line-break is encountered
            self.row += 1  # increment row to connote the position has advanced onto the next line in a file, item in a list, etc.
            self.column = resetValue  # reset column to the resetValue to begin tracking the position from the beginning again

        else:
            # if no line-break is encountered then the row attribute doesn't need to be altered
            self.column += 1  # increment column to move onto the next position in the line, item, etc.
            
