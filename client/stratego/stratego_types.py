from typing import Literal

from game_types import SCREEN_WIDTH, gen_flipped_dict

# The dimensions of a Stratego board.
ROWS = 10
COLS = 10

# The number of rows on a player's starting Stratego deck.
DECK_ROWS = 4

# The size of a Stratego piece's sprite.
SPRITE_WIDTH = 32
SPRITE_HEIGHT = 32

# The starting point of the Stratego grid's rendering.
# NOTE: The x coordinate of this tuple computes the starting coordinate such that 
# the grid renders in the center of the screen.
# The y coordinate is arbitrary, it just serves as padding.
GRID_START_LOCATION = (SCREEN_WIDTH // 2 - (SPRITE_WIDTH * ROWS) // 2, 16)

Color = Literal['r', 'b']
PieceName = Literal['bomb', 'captain', 'coronel', 'flag', 'general', 'lieutenant', 'major', 'marshal', 'miner', 'scout', 'sergeant', 'spy']

def get_full_color_name(color: Color) -> str:
    if color == 'r':
        return "red"
    elif color == 'b':
        return "blue"
    else:
        # Unreachable.
        raise Exception(f"unexpected color: {color}")

class StrategoPlayerInfo:
    """
    The client-side type for the Player. 
    """

    def __init__(self, username: str, starting_deck_str_repr: str):
        self.username = username
        self.starting_deck_repr = starting_deck_str_repr


class Board:
    """
    The client-side type for the board. In constrast to the server, this class 
    stores its elements in a flat array since that is the format that the socket 
    messages use to receive the board from the server each turn.
    """

    def __init__(self):
        self.elements = ['0' for _ in range(ROWS * COLS)]
        
    
    def to_socket_msg_repr(self) -> str:
        """
        Turns the board into a socket-friendly colon-delimited string format.
        """
        return _flat_array_to_message_repr(self.elements)
    
    
    def update_elements_with_socket_repr(self, socket_repr: str):
        """
        Updates the board's elements using the given socket string representation of a board.
        """
        self.elements = _message_repr_to_flat_array(socket_repr)


def temp_generate_placeholder_deck() -> list[str]:
    deck = [
        ['8', '5', 'G', '1', 'C', '3', 'B', 'B', 'B', 'B'],
        ['4', '2', 'L', 'S', '8', 'L', '4', '8', '3', '2'],
        ['8', '5', '8', 'L', 'C', '4', 'C', '5', 'C', '4'],
        ['F', 'B', '3', 'B', '5', '8', 'L', '2', '8', '5'],
    ]
    return _flatten_2d_array(deck)


def _flatten_2d_array(array: list[list[str]]) -> list[str]:
    ls = []
    for row in array:
        ls.extend(row)

    return ls


def deck_to_socket_message_repr(deck: list[str]):
    return _flat_array_to_message_repr(deck)


def _flat_array_to_message_repr(flat_array: list[str] ) -> str:
    return ':'.join(flat_array)


def _message_repr_to_flat_array(message_repr: str) -> list[str]:
    return message_repr.split(':')


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
    'marshal': 1,
    'general': 1,
    'coronel': 2,
    'major': 3,
    'captain': 4,
    'lieutenant': 4,
    'sergeant': 4,
    'scout': 8,
    'miner': 5,
    'bomb': 6,
    'flag': 1,
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