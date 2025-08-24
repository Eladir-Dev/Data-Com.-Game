from socket import socket

# Re-export Python's `socket` type under a different name so that it doesn't conflict with
# the name of the module, which is also named `socket`.
Connection = socket

# The size of the socket's buffer for receiving and sending messages 
# between the server and the client.
BUF_SIZE = 1024

def row_col_to_flat_index(r: int, c: int, logical_cols: int) -> int:
    """
    Maps 2D row-column coodinates to an index into a 'flat' (1D) array.
    This function needs the number of columns in the 2D array to compute the final index.
    """
    return r * logical_cols + c


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