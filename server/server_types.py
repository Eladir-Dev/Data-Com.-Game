from socket import socket
from typing import Literal

# Re-export Python's `socket` type under a different name so that it doesn't conflict with
# the name of the module, which is also named `socket`.
Connection = socket

class ColorCode:
    """
    This class which defines some terminal color codes as constants.
    """

    # Text (foreground) colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    RESET = "\033[0m"  # to reset the color

    # Background colors
    BACKGROUND_RED = "\033[41m"
    BACKGROUND_GREEN = "\033[42m"
    BACKGROUND_YELLOW = "\033[43m"
    BACKGROUND_BLUE = "\033[44m"
    BACKGROUND_MAGENTA = "\033[45m"
    BACKGROUND_CYAN = "\033[46m"
    BACKGROUND_WHITE = "\033[47m"

# The size of the socket's buffer for receiving and sending messages 
# between the server and the client.
BUF_SIZE = 1024

def row_col_to_flat_index(r: int, c: int, logical_cols: int) -> int:
    """
    Maps 2D row-column coodinates to an index into a 'flat' (1D) array.
    This function needs the number of columns in the 2D array to compute the final index.
    """
    return r * logical_cols + c


def get_sign(num: int) -> Literal[0, 1, -1]:
    """
    Returns the sign of the given number. 
    * 1 if positive
    * -1 if negative
    * 0 if the given number is 0.
    """

    if num < 0:
        return -1
    elif num > 0:
        return 1
    else:
        return 0


from typing import TypeVar

K = TypeVar('K')
V = TypeVar('V')
def gen_flipped_dict(dict_: dict[K, V]) -> dict[V, K]:
    """
    Flips the given dictionary, such that the keys are now the values 
    and the values are now the keys. Note: this function assumes that all the values are unique, 
    if they aren't, the resulting string will erase duplicate key-value pairs which shared a value in 
    the original dictionary.
    """
    return { dict_[k]: k for k in dict_ }