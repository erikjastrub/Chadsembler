"""
Module containing the 'SymbolTable' class which contains a nested 'SymbolTableEntry' class
"""

from defaults import Defaults
from symboltableentry import SymbolTableEntry

class SymbolTable:
    """
    -Class encapsulating all functionality needed to access and manipulate symbols in a safe, routine way
    """

    # --Static Members (Belong to the class and not an individual class instance)
    BRANCH_LABEL: int = 1  # The identifier of a label to branch to
    VARIABLE_LABEL: int = 2  # The identifier of a variable
    PROCEDURE_LABEL: int = 3  # The identifier of a procedure

    # --Class Members / Object Attributes
    SYMBOL_TABLE: dict[str, SymbolTableEntry]

    # --Object Methods
    def __init__(self: "SymbolTable") -> None:
        """Constructor for a `SymbolTable` object"""
        
        # Under the hood, the symbol table is just a dictionary, mapping labels to its contextual information
        # The SymbolTable class is used to ensure the symbol table is manipulated in a routine way
        # This is so symbols themselves cannot be modified outside of the class improperly
        # Using a class allows for the symbol table to be encapsulated allowing for this
        self.__SYMBOL_TABLE: dict[str, SymbolTableEntry] = {}  # Instantiate a new, empty dictionary

    
    def insert(self: "SymbolTable", labelIdentifier: str, labelValue: int, labelType: int):
        """Will insert a new SymbolTableEntry into the symbol table"""

        # Convert the labelIdentifier (key) into its default-case form
        # Then hash it and insert a SymbolTableEntry object containing all contextual information into the underlying symbol table
        self.__SYMBOL_TABLE[Defaults.convertToCasing(labelIdentifier)] = SymbolTableEntry(labelIdentifier, labelValue, labelType)

    def get(self: "SymbolTable", targetLabelIdentifier: str) -> SymbolTableEntry | Defaults.NULL:
        """Controls the way symbols from the symbol table are accessed, ensuring the symbol table is manipulated in a routine way"""

        try:
            
            # Convert the key into its default cased form before attempting to access it
            # All keys are stored in its default cased form
            return self.__SYMBOL_TABLE[Defaults.convertToCasing(targetLabelIdentifier)]

        except KeyError:

            # Return NULL to indicate the key doesn't exist in the dictionary
            # Returning NULL indicates a NULL reference like that found in other languages like C / C++ and Java
            return Defaults.NULL

    def getLabels(self: "SymbolTable"):
        """getter method, providing access to all the keys (labels) in the symbol table"""

        return self.__SYMBOL_TABLE.keys()  # Get all the keys and return them to the caller