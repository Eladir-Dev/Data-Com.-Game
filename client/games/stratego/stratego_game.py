"""
This module is for displaying the Stratego board on a game window.
"""

import pygame
from pygame import Surface, Rect
from pygame.event import Event
from pathlib import Path

from common_types.global_state import StrategoGlobalState, apply_ui_scale_pair, apply_ui_scale_int

from .stratego_types import (StrategoRenderedTile, ROWS, COLS, GRID_START_LOCATION, SPRITE_WIDTH, 
                             SPRITE_HEIGHT, StrategoColor, StrategoPieceName, get_full_color_name, parse_piece_from_encoded_str, assert_str_is_color, encoded_str_is_empty, encoded_str_is_lake)

from common_types.game_types import Pair, row_col_to_flat_index
import ui.drawing_utils as drawing_utils


def get_sprite_dimesions(ui_scale: float) -> Pair:
    return apply_ui_scale_pair((SPRITE_WIDTH, SPRITE_HEIGHT), ui_scale)


SPRITE_FOLDER = Path(__file__).parent / "assets"


def draw_empty_grid_slot(surface: Surface, location: Pair, sprite_dimensions: Pair) -> Rect:
    """
    Draws an empty grid slot at :py:attr:`location`.
    """
    empty_space_sprite = pygame.image.load(f"{SPRITE_FOLDER}/empty_space.png")
    return drawing_utils.draw_sprite_on_surface(surface, empty_space_sprite, location, sprite_dimensions)


def draw_lake_slot(surface: Surface, location: Pair, sprite_dimensions: Pair) -> Rect:
    """
    Draws a lake slot at :py:attr:`location`.
    """
    empty_space_sprite = pygame.image.load(f"{SPRITE_FOLDER}/lake.png")
    return drawing_utils.draw_sprite_on_surface(surface, empty_space_sprite, location, sprite_dimensions)


def draw_hidden_slot(surface: Surface, location: Pair, sprite_dimensions: Pair) -> Rect:
    """
    Draws a hidden slot at :py:attr:`location`.
    """
    empty_space_sprite = pygame.image.load(f"{SPRITE_FOLDER}/hidden.png")
    return drawing_utils.draw_sprite_on_surface(surface, empty_space_sprite, location, sprite_dimensions)


def draw_piece(surface: Surface, piece_name: StrategoPieceName, color: StrategoColor, location: Pair, sprite_dimensions: Pair) -> Rect:
    """
    Draws the sprite corresponding with :py:attr:`piece_name` at :py:attr:`location`.
    """
    piece_sprite = pygame.image.load(f"{SPRITE_FOLDER}/{get_full_color_name(color)}_{piece_name}.png")
    return drawing_utils.draw_sprite_on_surface(surface, piece_sprite, location, sprite_dimensions)


def gen_move_cmd(from_pos: Pair, to_pos: Pair) -> str:
    """
    Generates a socket-friendly move command using the given start and end positions.
    """
    components = [from_pos[0], from_pos[1], to_pos[0], to_pos[1]]
    components_str = ':'.join(str(c) for c in components)
    return f"!move:{components_str}\\"


def draw_ui_text(surface: Surface, global_game_data: StrategoGlobalState):
    heading_font_size = 100
    drawing_utils.draw_text(
        surface, 
        "Stratego", 
        apply_ui_scale_int(heading_font_size, global_game_data.ui_scale), 
        (surface.get_width() // 2, apply_ui_scale_int(50, global_game_data.ui_scale)), 
        (0, 0, 0),
    )

    info_string_font_size = 40

    player_info_string = f"{global_game_data.own_username} ({global_game_data.own_color}) VS {global_game_data.opp_username} ({global_game_data.opp_color})"
    drawing_utils.draw_text(
        surface, 
        player_info_string, 
        apply_ui_scale_int(info_string_font_size, global_game_data.ui_scale), 
        (surface.get_width() // 2, apply_ui_scale_int(120 + ROWS * SPRITE_HEIGHT, global_game_data.ui_scale)), 
        (0, 0, 0),
    )

    turn_info_string = f"Current Turn: ({global_game_data.turn})"
    drawing_utils.draw_text(
        surface, 
        turn_info_string, 
        apply_ui_scale_int(info_string_font_size, global_game_data.ui_scale), 
        (surface.get_width() // 2, apply_ui_scale_int(170 + ROWS * SPRITE_HEIGHT, global_game_data.ui_scale)), 
        (0, 0, 0),
    )

    selected_piece_font_size = 40

    if global_game_data.last_selected_piece is not None:
        # NOTE: we can get index 1 as `last_selected_piece` cannot be an empty tile which is `""`.
        piece_name = parse_piece_from_encoded_str(global_game_data.last_selected_piece.str_encoding[1])
        r, c = global_game_data.last_selected_piece.board_location
        selected_piece_str = f"{piece_name.title()} (row {r + 1}, column {c + 1})"

    else:
        selected_piece_str = "None"

    drawing_utils.draw_text(
        surface,
        f"Selected Piece: {selected_piece_str}",
        apply_ui_scale_int(selected_piece_font_size, global_game_data.ui_scale),
        (surface.get_width() // 2, apply_ui_scale_int(210 + ROWS * SPRITE_HEIGHT, global_game_data.ui_scale)), 
        (0, 0, 0),
    )


def stratego_update(events: list[Event], surface: Surface, global_game_data: StrategoGlobalState) -> str | None:
    """
    Updates the screen during a Stratego game.
    """
    # Set screen caption.
    pygame.display.set_caption(f"Stratego")

    # Clear the screen.
    surface.fill((100, 100, 100))

    # TODO: Only for testing out move result detection.
    # TODO: Add a better indicator for the kind of move result.
    move_result = global_game_data.current_move_result
    if move_result is not None:
        if move_result.kind == 'attack_success':
            surface.fill((0, 100, 0))

        elif move_result.kind == 'attack_fail':
            surface.fill((100, 0, 0))

        elif move_result.kind != 'movement':
            surface.fill((0, 0, 0))

    draw_ui_text(surface, global_game_data)

    rendered_tiles = render_board_tiles(surface, global_game_data)

    move_cmd: str | None = None

    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            print(mouse_pos)
            
            for rendered_tile in rendered_tiles:
                sprite_rect = rendered_tile.sprite_rect

                if sprite_rect.collidepoint(mouse_pos):
                    if global_game_data.last_selected_piece is None:
                        # Empty and lake tiles are not selectable.
                        if encoded_str_is_empty(rendered_tile.str_encoding) or encoded_str_is_lake(rendered_tile.str_encoding):
                            continue

                        # The opponent's pieces are non-selectable.
                        piece_color: StrategoColor = assert_str_is_color(rendered_tile.str_encoding[0])
                        if global_game_data.own_color != piece_color:
                            continue

                        # Select the tile.
                        global_game_data.last_selected_piece = rendered_tile

                    else:
                        from_pos = global_game_data.last_selected_piece.board_location
                        to_pos = rendered_tile.board_location

                        move_cmd = gen_move_cmd(from_pos, to_pos)

                        # Un-select the tile.
                        global_game_data.last_selected_piece = None

    return move_cmd


def render_board_tiles(surface: Surface, global_game_data: StrategoGlobalState) -> list[StrategoRenderedTile]:
    """
    Renders the board tiles in :py:attr:`global_game_data.board` from the server and returns them in 
    such a way so that they can be clicked and selected.
    """
    own_color = global_game_data.own_color
    move_result = global_game_data.current_move_result

    rendered_tiles: list[StrategoRenderedTile] = []

    for r in range(ROWS):
        for c in range(COLS):
            flat_idx = row_col_to_flat_index(r, c, COLS)
            encoded_element_str = global_game_data.board.elements[flat_idx]

            # For Pygame's coordinate system.
            if own_color == 'r':
                x, y = c, r
            else:
                # Mirror the row/col coordiantes (w.r.t. to the board) so that 
                # the blue player's pieces render from a 180 degree POV on the Pygame screen.
                x, y = -(c + 1) % COLS, -(r + 1) % ROWS

            location = apply_ui_scale_pair(
                (GRID_START_LOCATION[0] + SPRITE_WIDTH * x, GRID_START_LOCATION[1] + SPRITE_HEIGHT * y), 
                global_game_data.ui_scale,
            )

            # Show the special move-result view when the move result exists (it being non-None indicates that 
            # the result should be visible). Filters out for when the move result indicates simple movement.
            should_show_move_view = move_result is not None and move_result.kind != 'movement'

            # Normal piece drawing mode. Own pieces are visible and opponent pieces are hidden.
            should_draw_own_piece_outside_of_attack = not should_show_move_view and encoded_element_str.startswith(own_color)

            # Drawing mode during an attack. Only the pieces involved in an attack are shown.
            should_draw_pieces_involved_in_attack = (
                should_show_move_view 
                and move_result is not None # redundant check since `should_show_move_view` already guarantees it
                and (r, c) in { move_result.attacking_pos, move_result.defending_pos }
            )

            if encoded_str_is_empty(encoded_element_str):
                sprite = draw_empty_grid_slot(
                    surface, 
                    location, 
                    get_sprite_dimesions(global_game_data.ui_scale),
                )

            elif encoded_str_is_lake(encoded_element_str):
                sprite = draw_lake_slot(
                    surface, 
                    location, 
                    get_sprite_dimesions(global_game_data.ui_scale),
                )

            elif (should_draw_own_piece_outside_of_attack or should_draw_pieces_involved_in_attack):
                color: StrategoColor = assert_str_is_color(encoded_element_str[0])
                encoded_piece_str = encoded_element_str[1] # just the piece encoding without the color

                piece_name = parse_piece_from_encoded_str(encoded_piece_str)
                sprite = draw_piece(
                    surface, 
                    piece_name, 
                    color, 
                    location, 
                    get_sprite_dimesions(global_game_data.ui_scale),
                )

            # Hide the opponent's pieces.
            else:
                sprite = draw_hidden_slot(surface, location, get_sprite_dimesions(global_game_data.ui_scale))

            rendered_tiles.append(StrategoRenderedTile(sprite, encoded_element_str, (r, c)))

    return rendered_tiles
