"""
This module is for displaying the Stratego board on a game window.
"""

import pygame
from pygame import Surface, Rect
from pygame.event import Event
from typing import Any

from .stratego_types import (Board, StrategoMoveResult, ROWS, COLS, GRID_START_LOCATION, SPRITE_WIDTH, 
                             SPRITE_HEIGHT, Color, PieceName, get_full_color_name, parse_piece_from_encoded_str)

from game_types import Pair, row_col_to_flat_index, SCREEN_WIDTH

class RenderedTile:
    def __init__(self, sprite_rect: Rect, str_encoding: str, board_location: Pair):
        self.sprite_rect = sprite_rect
        self.str_encoding = str_encoding
        self.board_location = board_location


def get_module_outer_path(script_file_path: str) -> str:
    """
    Utility function for getting the outer path of the given script path 
    (i.e. gets the directory that the file given by `__file__` is in). 
    """
    return '\\'.join(script_file_path.split('\\')[:-1])


def draw_sprite_on_surface(surface: Surface, sprite: Surface, location: Pair, target_dimensions: Pair = (SPRITE_WIDTH, SPRITE_HEIGHT)) -> Rect:
    scaled = pygame.transform.scale(sprite, target_dimensions)
    sprite_rect = scaled.get_rect(topleft=location)
    surface.blit(scaled, sprite_rect)
    return sprite_rect


SPRITE_FOLDER = f"{get_module_outer_path(__file__)}/assets"


def draw_text(surface: Surface, text: str, font_size: int, location: Pair, color: tuple[int, int, int]):
    font = pygame.font.SysFont(None, font_size)
    text_surface = font.render(text, True, color)

    # Make `location` be the center.
    text_rect = text_surface.get_rect(center=location)
    surface.blit(text_surface, text_rect)


def draw_empty_grid_slot(surface: Surface, location: Pair) -> Rect:
    empty_space_sprite = pygame.image.load(f"{SPRITE_FOLDER}/empty_space.png")
    return draw_sprite_on_surface(surface, empty_space_sprite, location)


def draw_lake_slot(surface: Surface, location: Pair) -> Rect:
    empty_space_sprite = pygame.image.load(f"{SPRITE_FOLDER}/lake.png")
    return draw_sprite_on_surface(surface, empty_space_sprite, location)


def draw_hidden_slot(surface: Surface, location: Pair) -> Rect:
    empty_space_sprite = pygame.image.load(f"{SPRITE_FOLDER}/hidden.png")
    return draw_sprite_on_surface(surface, empty_space_sprite, location)


def draw_piece(surface: Surface, piece_name: PieceName, color: Color, location: Pair) -> Rect:
    piece_sprite = pygame.image.load(f"{SPRITE_FOLDER}/{get_full_color_name(color)}_{piece_name}.png")
    return draw_sprite_on_surface(surface, piece_sprite, location)


def gen_move_cmd(from_pos: Pair, to_pos: Pair) -> str:
    components = [from_pos[0], from_pos[1], to_pos[0], to_pos[1]]
    components_str = ':'.join(str(c) for c in components)
    return f"!move:{components_str}"


def stratego_update(events: list[Event], surface: Surface, global_game_data: dict[str, Any]) -> str | None:
    # Get state.
    own_color = global_game_data['stratego_state']['own_color']
    opponent_color = 'r' if own_color == 'b' else 'b'
    opponent_username = global_game_data['stratego_state']['opponent_username']
    turn = global_game_data['stratego_state']['turn']

    # Set screen caption.
    pygame.display.set_caption(f"Stratego")

    # Clear the screen.
    surface.fill((100, 100, 100))

    # TODO: Only for testing out move result detection.
    # TODO: Add a better indicator for the kind of move result.
    move_result: StrategoMoveResult | None = global_game_data['stratego_state']['current_move_result']
    if move_result is not None:
        if move_result.kind == 'attack_success':
            surface.fill((0, 100, 0))

        elif move_result.kind == 'attack_fail':
            surface.fill((100, 0, 0))

        else:
            surface.fill((0, 0, 0))

    # Draw UI text.
    draw_text(surface, "Stratego", 100, (SCREEN_WIDTH // 2, 50), (0, 0, 0))

    player_info_string = f"{global_game_data['username']} ({own_color}) VS {opponent_username} ({opponent_color})"
    draw_text(surface, player_info_string, 40, (SCREEN_WIDTH // 2, 120 + ROWS * SPRITE_HEIGHT), (0, 0, 0))

    turn_info_string = f"Current Turn: ({turn})"
    draw_text(surface, turn_info_string, 40, (SCREEN_WIDTH // 2, 170 + ROWS * SPRITE_HEIGHT), (0, 0, 0))

    # Get the board from the global state.
    board: Board = global_game_data['stratego_state']['board']

    rendered_tiles = render_board_tiles(surface, global_game_data, board)

    move_cmd: str | None = None

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            print(mouse_pos)
            
            for rendered_tile in rendered_tiles:
                sprite_rect = rendered_tile.sprite_rect

                if sprite_rect.collidepoint(mouse_pos):
                    # TODO: Do not print these out in an actual game, it 
                    # would ruin the entire point of hiding the opponent's pieces.
                    print(rendered_tile.str_encoding)

                    if global_game_data['stratego_state']['last_selected_piece'] is None:
                        # Select the tile.
                        global_game_data['stratego_state']['last_selected_piece'] = rendered_tile

                    else:
                        from_pos = global_game_data['stratego_state']['last_selected_piece'].board_location
                        to_pos = rendered_tile.board_location

                        move_cmd = gen_move_cmd(from_pos, to_pos)

                        global_game_data['stratego_state']['last_selected_piece'] = None

    return move_cmd


def render_board_tiles(surface: Surface, global_game_data: dict[str, Any], board: Board) -> list[RenderedTile]:
    own_color: Color = global_game_data['stratego_state']['own_color']
    move_result: StrategoMoveResult | None = global_game_data['stratego_state']['current_move_result']

    rendered_tiles: list[RenderedTile] = []

    for r in range(ROWS):
        for c in range(COLS):
            flat_idx = row_col_to_flat_index(r, c, COLS)
            encoded_element_str = board.elements[flat_idx]

            # For Pygame's coordinate system.
            if own_color == 'r':
                x, y = c, r
            else:
                # Mirror the row/col coordiantes (w.r.t. to the board) so that 
                # the blue player's pieces render from a 180 degree POV on the Pygame screen.
                x, y = -(c + 1) % COLS, -(r + 1) % ROWS

            location = (GRID_START_LOCATION[0] + SPRITE_WIDTH * x, GRID_START_LOCATION[1] + SPRITE_HEIGHT * y)

            # Normal piece drawing mode. Own pieces are visible and opponent pieces are hidden.
            should_draw_own_piece_outside_of_attack = move_result is None and encoded_element_str.startswith(own_color)

            # Drawing mode during an attack. Only the pieces involved in an attack are shown.
            should_draw_pieces_involved_in_attack = move_result is not None and (r, c) in { move_result.attacking_pos, move_result.defending_pos }

            if encoded_element_str == "":
                sprite = draw_empty_grid_slot(surface, location)

            elif encoded_element_str == "XX":
                sprite = draw_lake_slot(surface, location)

            elif len(encoded_element_str) >= 2 and (should_draw_own_piece_outside_of_attack or should_draw_pieces_involved_in_attack):
                color: Color = encoded_element_str[0] # type: ignore
                encoded_piece_str = encoded_element_str[1] # just the piece encoding without the color

                piece_name = parse_piece_from_encoded_str(encoded_piece_str)
                sprite = draw_piece(surface, piece_name, color, location)

            # Hide the opponent's pieces.
            elif len(encoded_element_str) >= 2:
                sprite = draw_hidden_slot(surface, location)

            # Fallback.
            else:
                sprite = draw_hidden_slot(surface, location)

            rendered_tiles.append(RenderedTile(sprite, encoded_element_str, (r, c)))

    return rendered_tiles
