from game_types import SCREEN_WIDTH

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
    deck = [str(i % COLS) for i in range(DECK_ROWS * COLS)]
    return deck


def deck_to_socket_message_repr(deck: list[str]):
    return _flat_array_to_message_repr(deck)


def _flat_array_to_message_repr(flat_array: list[str] ) -> str:
    return ':'.join(flat_array)


def _message_repr_to_flat_array(message_repr: str) -> list[str]:
    return message_repr.split(':')

