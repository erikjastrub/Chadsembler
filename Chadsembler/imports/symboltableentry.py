"""
Module containing the 'SymbolTableEntry' class
"""

class SymbolTableEntry:
    """
    -A class encapsulating all symbol related data, to be used as an entry by the SymbolTable class
    """
    
    # --Class Members / Object Attributes
    labelIdentifier: str
    labelValue: int
    labelType: int

    # --Object Methods
    def __init__(self: "SymbolTableEntry", labelIdentifier: str, labelValue: int, labelType: int) -> None:
        """Constructor for a `SymbolTableEntry` object"""

        self.labelIdentifier: str = labelIdentifier  # The actual name of the label
        self.labelValue: int = labelValue  # The value associated with the label
        self.labelType: int = labelType  # The type of label, can either be 1 of 3 types: Branch, Variable or Procedure label
