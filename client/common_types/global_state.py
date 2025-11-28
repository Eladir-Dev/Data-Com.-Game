from dataclasses import dataclass
from typing import Literal
from common_types.game_types import Pair
from games.stratego.stratego_types import StrategoColor, StrategoBoard, StrategoMoveResult, StrategoRenderedTile, toggle_color
from games.secret_game.secret_game_types import SecretGamePlayer, SecretGameMap, TurnState
from games.lore.lore_types import LoreKind, LoreMap, map_pos_to_real_pos

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
    'in_secret_dlc_store',
    'in_secret_dlc_game',
    'in_secret_paint_game',
    'in_lore',
]

class StrategoGlobalState:
    def __init__(self, own_color: StrategoColor, own_username: str, opponent_username: str, ui_scale: float):
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

        self.ui_scale = ui_scale


class WordGolfGlobalState:
    def __init__(self, own_username: str, opponent_username: str, ui_scale: float):
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

        self.ui_scale = ui_scale

    
class SecretGameGlobalState:
    def __init__(self, own_idx: int, players: list[SecretGamePlayer], map: SecretGameMap, ui_scale: float):
        self.own_idx = own_idx
        self.players = players
        self.map = map
        self.turn_state: TurnState = 'straight'

        self.countdown: int | None = None

        self.ui_scale = ui_scale


    def get_own_data(self) -> SecretGamePlayer:
        return self.players[self.own_idx]
    

    def get_opp_data(self) -> SecretGamePlayer:
        return self.players[(self.own_idx + 1) % 2]


class LoreGlobalState:
    def __init__(self, username: str, ui_scale: float, kind: LoreKind):
        self.username = username
        self.ui_scale = ui_scale
        self.kind: LoreKind = kind
        self.map = LoreMap(kind)

        self.player_pos: tuple[float, float] = map_pos_to_real_pos(self.map.player_spawn_map_pos)
        self.player_speed: float = 5.0 # tiles per second

    
    def get_player_pos(self) -> Pair:
        return (int(self.player_pos[0]), int(self.player_pos[1]))


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
    lore_state: LoreGlobalState | None = None
    """
    Holds Lore-specific state.
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

    pending_ui_scale: float = 1.0
    ui_scale: float = 1.0

    pending_volume: float = 100.0
    volume: float = 100.0

    can_see_secret_game_menu: bool = False
    can_see_secret_dlc_store: bool = False
    can_see_secret_web_game_menu: bool = False

    secret_dlc_download_percentage: float = 0.0
    is_already_downloading_dlc: bool = False

