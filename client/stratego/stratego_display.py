"""
This module is for displaying the Stratego board on a game window.
"""

import pygame
from pygame import Surface
from pygame.event import Event
from typing import Any

from queue import Queue

from .stratego_types import (Board, ROWS, COLS, GRID_START_LOCATION, SPRITE_WIDTH, 
                             SPRITE_HEIGHT, Color, PieceName, get_full_color_name, parse_piece_from_encoded_str)

from game_types import Pair, row_col_to_flat_index

# TODO: Change this class so that it just contains the encoded string. This way it 
# can be used for empty space and lake tiles.
class RenderedPiece:
    def __init__(self, sprite: Surface, name: PieceName, color: Color):
        self.sprite = sprite
        self.name = name
        self.color = color


def get_module_outer_path(script_file_path: str) -> str:
    """
    Utility function for getting the outer path of the given script path 
    (i.e. gets the directory that the file given by `__file__` is in). 
    """
    return '\\'.join(script_file_path.split('\\')[:-1])


def draw_sprite_on_surface(surface: Surface, sprite: Surface, location: Pair, target_dimensions: Pair = (SPRITE_WIDTH, SPRITE_HEIGHT)):
    scaled = pygame.transform.scale(sprite, target_dimensions)
    surface.blit(scaled, location)
    return scaled


SPRITE_FOLDER = f"{get_module_outer_path(__file__)}/assets"


def draw_empty_grid_slot(surface: Surface, location: Pair):
    empty_space_sprite = pygame.image.load(f"{SPRITE_FOLDER}/empty_space.png")
    draw_sprite_on_surface(surface, empty_space_sprite, location)


def draw_lake_slot(surface: Surface, location: Pair):
    empty_space_sprite = pygame.image.load(f"{SPRITE_FOLDER}/lake.png")
    draw_sprite_on_surface(surface, empty_space_sprite, location)


def draw_hidden_slot(surface: Surface, location: Pair):
    empty_space_sprite = pygame.image.load(f"{SPRITE_FOLDER}/hidden.png")
    return draw_sprite_on_surface(surface, empty_space_sprite, location)


def draw_piece(surface: Surface, piece_name: PieceName, color: Color, location: Pair):
    piece_sprite = pygame.image.load(f"{SPRITE_FOLDER}/{get_full_color_name(color)}_{piece_name}.png")
    return draw_sprite_on_surface(surface, piece_sprite, location)


def stratego_update(events: list[Event], surface: Surface, global_game_data: dict[str, Any], server_command_queue: Queue[str], client_queue: Queue[str]):
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

    # TODO: Currently this only returns the player's own pieces. The opponents pieces, empty 
    # spaces, and lakes are not accounted for.
    rendered_pieces = display_board_grid(surface, global_game_data, server_command_queue, client_queue, board)

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            print(mouse_pos)
            
            # This is the "event-driven" check you're looking for
            # Loop through all your sprites
            for rendered_piece in rendered_pieces:
                sprite = rendered_piece.sprite

                # TODO: This isn't working, the sprites act as if they're at (0, 0).
                # The mouse click detection and position works fine though.
                if sprite.get_rect().collidepoint(mouse_pos):
                    print(f"CLICKED: '{rendered_piece.color} {rendered_piece.name}'")


def display_board_grid(surface: Surface, global_game_data: dict[str, Any], server_command_queue: Queue[str], client_queue: Queue[str], board: Board):
    own_color: Color = global_game_data['stratego_state']['own_color']

    # TODO: Add ALL the rendered tiles to this list; not just own colored pieces.
    rendered_pieces: list[RenderedPiece] = []

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

            elif len(element) >= 2 and element.startswith(own_color):
                encoded_piece_str = element[1]
                piece_name = parse_piece_from_encoded_str(encoded_piece_str)
                piece_sprite = draw_piece(surface, piece_name, own_color, location)

                rendered_pieces.append(RenderedPiece(piece_sprite, piece_name, own_color))

            # Hide the opponent's pieces.
            elif len(element) >= 2:
                draw_hidden_slot(surface, location)

            else:
                draw_empty_grid_slot(surface, location)

    return rendered_pieces
