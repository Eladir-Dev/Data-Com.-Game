from typing import Literal
from server_types import gen_flipped_dict

# === Types ===

# The color of a Stratego player or piece.
StrategoColor = Literal['r', 'b']
PieceName = Literal['bomb', 'captain', 'coronel', 'flag', 'general', 'lieutenant', 'major', 'marshal', 'miner', 'scout', 'sergeant', 'spy']

Pair = tuple[int, int]

# === Constants ===

# The dimensions of a board.
ROWS = 10
COLS = 10

# The amount of rows that a player's starting deck has.
DECK_ROWS = 4

ENCODED_STR_TO_PIECE: dict[str, PieceName] = {
    'S': 'spy',
    '1': 'marshal',
    'G': 'general',
    '2': 'coronel',
    '3': 'major',
    'C': 'captain',
    'L': 'lieutenant',
    '4': 'sergeant',
    '8': 'scout',
    '5': 'miner',
    'B': 'bomb',
    'F': 'flag',
}

PIECE_TO_ENCODED_STR: dict[PieceName, str] = gen_flipped_dict(ENCODED_STR_TO_PIECE)

PIECE_TO_VALUE: dict[PieceName, int] = {
    'spy': 1,
    'marshal': 10,
    'general': 9,
    'coronel': 8,
    'major': 7,
    'captain': 6,
    'lieutenant': 5,
    'sergeant': 4,
    'scout': 2,
    'miner': 3,
    'bomb': 999,
    'flag': 0,
}

def parse_piece_from_encoded_str(encoded_str: str) -> PieceName:
    """
    Encoding legend:
    * 'S' = Spy (1)
    * '1' = Marshal (1)
    * 'G' = General (1)
    * '2' = Coronel (2)
    * '3' = Major (3)
    * 'C' = Captain (4)
    * 'L' = Lieutenant (4)
    * '4' = Sargeant (4)
    * '8' = Scout (8)
    * '5' = Miner (5)
    * 'B' = Bomb (6)
    * 'F' = Flag (1)
    """
    piece = ENCODED_STR_TO_PIECE.get(encoded_str)
    if piece is None:
        raise Exception(f"Unknown encoded piece string: '{encoded_str}'")
    
    return piece


def get_piece_value(piece: PieceName) -> int:
    value = PIECE_TO_VALUE.get(piece)
    if value is None:
        raise Exception(f"Got unexpected piece '{piece}'")
    
    return value