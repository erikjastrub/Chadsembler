class InstructionPool:
    """
    Class encapsulating all instruction pool related data, logically binding them together into a single entity
    Used by the Parser class to make accessing instruction pool related data much easier
    """

    # --Class Members / Object Attributes
    poolIdentifier: str
    tokenStream: list["TypedToken"]
    symbolTable: "SymbolTable"
    
    # --Object Methods
    def __init__(self, poolIdentifier, tokenStream, symbolTable):
        """Constructor for an `InstructionPool` object"""
        self.poolIdentifier: str = poolIdentifier
        self.tokenStream: list["TypedToken"] = tokenStream
        self.symbolTable: "SymbolTable" = symbolTable
