"""
Module used to check the version of the python interpreter
When a module is imported in python, 
    the file is ran to generate the functions, classes any variables, etc.
As ALL code is ran, if the code has any external effects 
    (such as asking for input, outputting something or in this case exiting the program)
The effects will affect the whole program
By importing this module the version of the interpreter is checked 
    and if it is too low the whole program will be exited out of
"""

# The 'sys' module contains the 'exit()' function needed to suspend the whole program
import sys
from colour import Colour

# Validate that minimum python 3.10 or above is being used to interpret the code
try: assert  sys.version_info.minor > 9

# If the validation failed then exit out of the whole program
except AssertionError: sys.exit(f"{Colour.RED}Python version too low, minimum python version 3.10.0 is needed to run this program{Colour.RESET}")
