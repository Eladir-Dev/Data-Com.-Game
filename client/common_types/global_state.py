from dataclasses import dataclass
from typing import Literal
from games.stratego.stratego_types import StrategoColor, StrategoBoard, StrategoMoveResult, StrategoRenderedTile, toggle_color
from games.secret_game.secret_game_types import SecretGamePlayer, Map

ValidState = Literal[
    'main_menu', 
    'loading_stratego_game',
    'in_stratego_game', 
    'loading_word_golf_game', 
    'in_word_golf_game',
    'loading_secret_game',
    'in_secret_game',
    'finished_game',
    'in_deck_selection_state',
]

class StrategoGlobalState:
    def __init__(self, own_color: StrategoColor, own_username: str, opponent_username: str):
        self.own_color: StrategoColor = own_color
        self.opp_color: StrategoColor = toggle_color(own_color)

        self.own_username = own_username
        self.opp_username = opponent_username

        # Empty board; gets filled in each turn with info from the server.
        self.board = StrategoBoard()

        # The red player always goes first.
        self.turn: StrategoColor = 'r'

        self.last_selected_piece: StrategoRenderedTile | None = None

        self.current_move_result: StrategoMoveResult | None = None


class WordGolfGlobalState:
    def __init__(self, own_username: str, opponent_username: str):
        self.own_username = own_username
        self.opp_username = opponent_username

        self.typed_letters: list[str] = []

        self.own_points = 0
        self.own_queued_word_amt = 0

        self.opp_points = 0
        self.opp_queued_word_amt = 0

        self.feedback_history: list[str] = []

        self.stashed_words: list[str] = []

        self.received_alerts: list[str] = []

    
class SecretGameGlobalState:
    def __init__(self, own_idx: int, players: list[SecretGamePlayer], map: Map):
        self.own_idx = own_idx
        self.players = players
        self.map = map


    def get_own_data(self) -> SecretGamePlayer:
        return self.players[self.own_idx]
    

    def get_opp_data(self) -> SecretGamePlayer:
        return self.players[(self.own_idx + 1) % 2]


@dataclass
class GlobalClientState:
    """
    The global client state of the application. Holds game specific 
    client data in the :py:attr:`stratego_state` and :py:attr:`word_golf_state` attributes.
    """

    username: str
    """
    The username of the player set in the generic main UI.
    """
    server_ip: str
    """
    The host name set by the player in the generic main UI.
    """
    game_state: ValidState
    """
    The current state of the application. Used mainly for determining 
    what screen should currently be displayed.
    """
    
    # Holds data related to the Stratego and Word Golf games once connected to the server.
    stratego_state: StrategoGlobalState | None = None
    """
    Holds Stratego-specific game data.
    """
    word_golf_state: WordGolfGlobalState | None = None
    """
    Holds Word Golf-specific game data.
    """
    secret_game_state: SecretGameGlobalState | None = None
    """
    Holds Secret Game-specific game state.
    """

    # Socket-representation of the starting deck.
    stratego_starting_deck_repr: str | None = None
    """
    Holds the socket-friendly representation of the starting deck that needs to be 
    set by the player (client) before trying to join a Stratego game on the server.
    """

    # Game-over message.
    game_over_message: str | None = None
    """
    A game-agnostic game over message that needs to be set after a game finishes.
    """