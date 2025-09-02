from dataclasses import dataclass
from typing import Literal

from pygame import Rect

from game_types import SCREEN_WIDTH, Pair, gen_flipped_dict

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
GRID_START_LOCATION = (SCREEN_WIDTH // 2 - (SPRITE_WIDTH * ROWS) // 2, 100)

StrategoColor = Literal['r', 'b']
StrategoPieceName = Literal['bomb', 'captain', 'coronel', 'flag', 'general', 'lieutenant', 'major', 'marshal', 'miner', 'scout', 'sergeant', 'spy']

@dataclass
class StrategoMoveResult:
    kind: Literal['movement', 'attack_success', 'attack_fail', 'tie']
    attacking_pos: Pair
    defending_pos: Pair

def get_full_color_name(color: StrategoColor) -> str:
    if color == 'r':
        return "red"
    elif color == 'b':
        return "blue"
    else:
        # Unreachable.
        raise Exception(f"unexpected color: {color}")
    
def toggle_color(color: StrategoColor) -> StrategoColor:
    return 'r' if color == 'b' else 'b'


def assert_str_is_color(string: str) -> StrategoColor:
    if string not in {'r', 'b'}:
        raise ValueError(f"String '{string}' is not a valid color")
    
    return string # type: ignore


@dataclass
class StrategoStartingPlayerInfo:
    """
    Starting data from the client for a Stratego player.
    """
    username: str
    starting_deck_repr: str


class StrategoBoard:
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


class StrategoRenderedTile:
    def __init__(self, sprite_rect: Rect, str_encoding: str, board_location: Pair):
        self.sprite_rect = sprite_rect
        self.str_encoding = str_encoding
        self.board_location = board_location


def temp_generate_placeholder_deck() -> list[str]:
    deck = [
        ['8', '5', 'G', '1', 'C', '3', 'B', 'B', 'B', 'B'],
        ['4', '2', 'L', 'S', '8', 'L', '4', '8', '3', '2'],
        ['8', '5', '8', 'L', 'C', '4', 'C', '5', 'C', '4'],
        ['F', 'B', '3', 'B', '5', '8', 'L', '2', '8', '5'],
    ]
    # Mirror the deck (row-wise) before flattening it so that the top rows face away from the player, instead of towards them.
    return _flatten_2d_array(deck[::-1])


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


ENCODED_STR_TO_PIECE: dict[str, StrategoPieceName] = {
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

PIECE_TO_ENCODED_STR: dict[StrategoPieceName, str] = gen_flipped_dict(ENCODED_STR_TO_PIECE)

def parse_piece_from_encoded_str(encoded_str: str) -> StrategoPieceName:
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
