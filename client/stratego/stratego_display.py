"""
This module is for displaying the Stratego board on a game window.
"""

import pygame
from pygame import Surface
from typing import Any

from queue import Queue

from .stratego_types import (Board, ROWS, COLS, GRID_START_LOCATION, SPRITE_WIDTH, 
                             SPRITE_HEIGHT, Color, PieceName, get_full_color_name, parse_piece_from_encoded_str)

from game_types import Pair, row_col_to_flat_index

def get_module_outer_path(script_file_path: str) -> str:
    """
    Utility function for getting the outer path of the given script path 
    (i.e. gets the directory that the file given by `__file__` is in). 
    """
    return '\\'.join(script_file_path.split('\\')[:-1])


def draw_sprite_on_surface(surface: Surface, sprite: Surface, location: Pair, target_dimensions: Pair = (SPRITE_WIDTH, SPRITE_HEIGHT)):
    scaled = pygame.transform.scale(sprite, target_dimensions)
    surface.blit(scaled, location)


SPRITE_FOLDER = f"{get_module_outer_path(__file__)}/assets"


def draw_empty_grid_slot(surface: Surface, location: Pair):
    empty_space_sprite = pygame.image.load(f"{SPRITE_FOLDER}/empty_space.png")
    draw_sprite_on_surface(surface, empty_space_sprite, location)


def draw_lake_slot(surface: Surface, location: Pair):
    empty_space_sprite = pygame.image.load(f"{SPRITE_FOLDER}/lake.png")
    draw_sprite_on_surface(surface, empty_space_sprite, location)


def draw_hidden_slot(surface: Surface, location: Pair):
    empty_space_sprite = pygame.image.load(f"{SPRITE_FOLDER}/hidden.png")
    draw_sprite_on_surface(surface, empty_space_sprite, location)


def draw_piece(surface: Surface, piece_name: PieceName, color: Color, location: Pair):
    piece_sprite = pygame.image.load(f"{SPRITE_FOLDER}/{get_full_color_name(color)}_{piece_name}.png")
    draw_sprite_on_surface(surface, piece_sprite, location)


def stratego_update(surface: Surface, global_game_data: dict[str, Any], server_command_queue: Queue[str], client_queue: Queue[str]):
    # Get state.
    own_color = global_game_data['stratego_state']['own_color']
    opponent_color = 'r' if own_color == 'b' else 'b'
    opponent_username = global_game_data['stratego_state']['opponent_username']
    turn = global_game_data['stratego_state']['turn']

    # Set screen caption with some state information (this info should be in a proper UI on the screen).
    pygame.display.set_caption(f"Stratego - {global_game_data['username']} ({own_color}) VS {opponent_username} ({opponent_color}) - Current Turn ({turn})")

    # Clear the screen with black.
    surface.fill((100, 100, 100))

    # Get the board from the global state.
    board: Board = global_game_data['stratego_state']['board']

    display_board_grid(surface, global_game_data, server_command_queue, client_queue, board)


def display_board_grid(surface: Surface, global_game_data: dict[str, Any], server_command_queue: Queue[str], client_queue: Queue[str], board: Board):
    # TODO: Read the elements of the board to render the sprites in a grid on the screen.

    own_color: Color = global_game_data['stratego_state']['own_color']

    for r in range(ROWS):
        for c in range(COLS):
            flat_idx = row_col_to_flat_index(r, c, COLS)
            element = board.elements[flat_idx]

            # For Pygame's coordinate system.
            if own_color == 'r':
                x, y = c, r
            else:
                # Mirror the row/col coordiantes (w.r.t. to the board) so that 
                # the blue player's pieces render from a 180 degree POV on the Pygame screen.
                x, y = -(c + 1) % COLS, -(r + 1) % ROWS

            location = (GRID_START_LOCATION[0] + SPRITE_WIDTH * x, GRID_START_LOCATION[1] + SPRITE_HEIGHT * y)

            if element == "":
                draw_empty_grid_slot(surface, location)
            elif element == "XX":
                draw_lake_slot(surface, location)
            # TODO: Actually draw the piece. Only lieutenants are drawn for now.
            elif len(element) >= 2 and element.startswith(own_color):
                encoded_piece_str = element[1]
                piece_name = parse_piece_from_encoded_str(encoded_piece_str)
                draw_piece(surface, piece_name, own_color, location)

            # Hide the opponent's pieces.
            elif len(element) >= 2:
                draw_hidden_slot(surface, location)
            else:
                draw_empty_grid_slot(surface, location)

