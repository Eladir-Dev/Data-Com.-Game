"""
This module is for displaying the Stratego board on a game window.
"""

import pygame
from pygame import Surface
from typing import Any

from queue import Queue

from .stratego_types import Board, ROWS, COLS, GRID_START_LOCATION, SPRITE_WIDTH, SPRITE_HEIGHT

from game_types import Pair

def get_module_outer_path(script_file_path: str) -> str:
    """
    Utility function for getting the outer path of the given script path 
    (i.e. gets the directory that the file given by `__file__` is in). 
    """
    return '\\'.join(script_file_path.split('\\')[:-1])


def draw_sprite_on_surface(surface: Surface, sprite: Surface, location: Pair, target_dimensions: Pair):
    scaled = pygame.transform.scale(sprite, target_dimensions)
    surface.blit(scaled, location)


PLACEHOLDER_SPRITE = pygame.image.load(f"{get_module_outer_path(__file__)}/assets/placeholder_sprite.png")

def stratego_update(surface: Surface, global_game_data: dict[str, Any], server_command_queue: Queue[str], client_queue: Queue[str]):
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

    display_board_grid(surface, global_game_data, server_command_queue, client_queue, board)


def display_board_grid(surface: Surface, global_game_data: dict[str, Any], server_command_queue: Queue[str], client_queue: Queue[str], board: Board):
    # TODO: Read the elements of the board to render the sprites in a grid on the screen.

    if global_game_data['stratego_state']['own_color'] == 'r':
        get_row_range = lambda: range(ROWS)
        get_col_range = lambda: range(COLS)
    
    else:
        # Return reversed ranges to view the board at a 180 degree view.
        get_row_range = lambda: reversed(range(ROWS))
        get_col_range = lambda: reversed(range(COLS))

    for r in get_row_range():
        for c in get_col_range():
            flat_idx = r * ROWS + c % COLS
            # TODO: Use the element on the board to render the sprite (somehow).
            # element = board.elements[flat_idx]

            location = (GRID_START_LOCATION[0] + SPRITE_WIDTH * r, GRID_START_LOCATION[1] + SPRITE_HEIGHT * c)

            draw_sprite_on_surface(surface, PLACEHOLDER_SPRITE, location, (SPRITE_WIDTH, SPRITE_HEIGHT))

