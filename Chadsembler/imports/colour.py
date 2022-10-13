"""
Module containing the 'Colour' class
"""

import os
os.system("color")

class Colour:
    """
    Class grouping together all ANSI colour codes and functionality to output colour to the terminal
    """
    RED_BACKGROUND: str = "\u001b[41m"

    BLACK: str = "\u001b[30m"
    RED: str = "\u001b[31m"
    GREEN: str = "\u001b[32m"
    YELLOW: str = "\u001b[33m"
    BLUE: str = "\u001b[34m"
    MAGENTA: str = "\u001b[35m"
    CYAN: str = "\u001b[36m"
    WHITE: str = "\u001b[37m"
    RESET: str = "\u001b[0m"
   
    @staticmethod
    def colourPrint(colour: str, text: str, end: str ='\n'):
        """Will output the text with the specified colour"""

        print(f"{colour}{text}{Colour.RESET}", end=end)

