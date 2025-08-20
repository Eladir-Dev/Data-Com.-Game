import pygame
from pygame import Surface
from typing import Any

from stratego_client import Board

ROWS = 10
COLS = 10

def stratego_update(surface: Surface, global_game_data: dict[str, Any]):
    # Get state.
    own_color = global_game_data['stratego_state']['own_color']
    opponent_color = 'r' if own_color == 'b' else 'b'
    opponent_username = global_game_data['stratego_state']['opponent_username']
    turn = global_game_data['stratego_state']['turn']

    # Set screen caption with some state information (this info should be in a proper UI on the screen).
    pygame.display.set_caption(f"Stratego - {global_game_data['username']} ({own_color}) VS {opponent_username} ({opponent_color}) - Current Turn ({turn})")

    # Clear the screen with black.
    surface.fill((0, 0, 0))

    # Get the board from the global state.
    board: Board = global_game_data['stratego_state']['board']

    # TODO: Read the elements of the board to render the sprites in a grid on the screen.
    for r in range(ROWS):
        for c in range(COLS):
            flat_idx = r * ROWS + c % COLS
            # print(f"{board.elements[flat_idx]} ", end='')

