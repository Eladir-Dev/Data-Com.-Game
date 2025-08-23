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