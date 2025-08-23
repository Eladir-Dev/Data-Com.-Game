"""
This module is for types and constants that are shared between games.
"""

# Dimensions in common for all games.
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400

# Utility type for games.
Pair = tuple[int, int]

# == Utility functions ==
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