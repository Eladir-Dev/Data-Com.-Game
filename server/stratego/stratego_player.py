from server_types import Connection
from .stratego_types import StrategoColor

class StrategoPlayer:
    """
    The server-side type for a Stratego player. Before a game starts, the server wraps the players' 
    connections in this class in the `conn` attribute. Also before the game starts, the clients send 
    the users' starting decks and the server decides each players' color. The server wraps all of these things 
    BEFORE the game starts in this class. 

    - `username` the username that the client sent to identify itself; is not unique
    - `starting_deck_repr` contains a colon-delimited string that represents the a player's starting deck (i.e. `"1:2:4:1:0"`)
    - `color` represents the player's color; this is decided automatically by the server

    Note that the starting decks are in a flat-array format. This means that all the rows of the deck are collapsed onto one row. 
    Also note that the deck is sent by the client and its pieces do not have color, as the client does not know the player's 
    color beforehand, as it is decided by the server.
    """

    def __init__(self, conn: Connection, username: str, starting_deck_repr: str, color: StrategoColor | None):
        self.conn = conn
        self.username = username
        self.color = color

        self.starting_deck_repr = starting_deck_repr