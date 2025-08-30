from dataclasses import dataclass
from typing import Literal
from stratego.stratego_types import StrategoColor, StrategoBoard, StrategoMoveResult, StrategoRenderedTile, toggle_color

ValidState = Literal[
    'main_menu', 
    'loading_stratego_game',
    'in_stratego_game', 
    'finished_stratego_game', 
    'in_wordle_game',
    'loading_wordle_game', 
    'finished_wordle_game',
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
    
@dataclass
class GlobalClientState:
    username: str
    game_state: ValidState
    stratego_state: StrategoGlobalState | None = None