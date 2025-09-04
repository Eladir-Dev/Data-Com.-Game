from dataclasses import dataclass
from typing import Literal
from stratego.stratego_types import StrategoColor, StrategoBoard, StrategoMoveResult, StrategoRenderedTile, toggle_color

ValidState = Literal[
    'main_menu', 
    'loading_stratego_game',
    'in_stratego_game', 
    'finished_stratego_game', 
    'in_word_golf_game',
    'loading_word_golf_game', 
    'finished_word_golf_game',
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

    
@dataclass
class GlobalClientState:
    username: str
    game_state: ValidState
    stratego_state: StrategoGlobalState | None = None
    word_golf_state: WordGolfGlobalState | None = None