"""
This module is for types and constants that are shared between games (client-side).
"""

from typing import Literal

# Dimensions in common for all games.
SCREEN_WIDTH = 900
"""
Width for the game screen.
"""
SCREEN_HEIGHT = 600
"""
Height for the game screen.
"""

# Utility type for games.
Pair = tuple[int, int]
"""
Utility type for a position in the game screen.
"""

CLIENT_FPS = 30

GameKind = Literal['stratego', 'word_golf', 'secret_game']

# == Utility functions ==
def row_col_to_flat_index(r: int, c: int, logical_cols: int) -> int:
    """
    Maps 2D row-column coodinates to an index into a 'flat' (1D) array.
    This function needs the number of columns in the 2D array to compute the final index.
    """
    return r * logical_cols + c


def gen_flipped_dict[K, V](dict_: dict[K, V]) -> dict[V, K]:
    """
    Flips the given dictionary, such that the keys are now the values 
    and the values are now the keys. Note: this function assumes that all the values are unique, 
    if they aren't, the resulting string will erase duplicate key-value pairs which shared a value in 
    the original dictionary.
    """
    return { dict_[k]: k for k in dict_ }