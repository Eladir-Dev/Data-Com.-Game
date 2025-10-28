from pygame.event import Event
from pygame import Surface
from common_types.global_state import SecretGameGlobalState
import pygame
from pathlib import Path
from ui.drawing_utils import draw_sprite_on_surface
from common_types.game_types import SCREEN_WIDTH, SCREEN_HEIGHT, Pair
from games.secret_game.secret_game_types import get_map_tile_sprite_name, map_pos_to_real_position, MAP_RESOLUTION
import math

SPITE_FOLDER = Path(__file__).parent / "assets"

def draw_map(surface: Surface, global_game_data: SecretGameGlobalState, camera_offset: Pair):
    tiles = global_game_data.map.tiles

    for r in range(len(tiles)):
        for c in range(len(tiles[r])):
            y, x = r, c
            tile_sprite = pygame.image.load(f"{SPITE_FOLDER}/{get_map_tile_sprite_name(tiles[r][c])}")

            real_pos = map_pos_to_real_position((x, y))

            draw_sprite_on_surface(
                surface,
                tile_sprite,
                (real_pos[0] + camera_offset[0], real_pos[1] + camera_offset[1]),
                (MAP_RESOLUTION, MAP_RESOLUTION),
                rect_origin='top_left',
            )

    draw_players(surface, global_game_data, camera_offset)


def draw_players(surface: Surface, global_game_data: SecretGameGlobalState, camera_offset: Pair):
    p1 = global_game_data.players[0]
    p2 = global_game_data.players[1]

    p1_angle_deg = p1.facing_angle * 180 / math.pi
    p2_angle_deg = p2.facing_angle * 180 / math.pi

    p1_sprite = pygame.transform.rotate(pygame.image.load(f"{SPITE_FOLDER}/player_01.png"), p1_angle_deg)
    p2_sprite = pygame.transform.rotate(pygame.image.load(f"{SPITE_FOLDER}/player_02.png"), p2_angle_deg)

    draw_sprite_on_surface(
        surface,
        p1_sprite,
        location=(p1.position[0] + camera_offset[0], p1.position[1] + camera_offset[1]),
        target_dimensions=(MAP_RESOLUTION, MAP_RESOLUTION),
        rect_origin='top_left',
    )

    draw_sprite_on_surface(
        surface,
        p2_sprite,
        location=(p2.position[0] + camera_offset[0], p2.position[1] + camera_offset[1]),
        target_dimensions=(MAP_RESOLUTION, MAP_RESOLUTION),
        rect_origin='top_left',
    )


def secret_game_update(events: list[Event], surface: Surface, global_game_data: SecretGameGlobalState):
    surface.fill((0, 0, 0))

    debug_string = f"{global_game_data.get_own_data().username} ({global_game_data.get_own_data().position}) " + \
        f"VS {global_game_data.get_opp_data().username} ({global_game_data.get_opp_data().position})"

    pygame.display.set_caption(debug_string)

    own_pos = global_game_data.get_own_data().position
    camera_offset = (SCREEN_WIDTH // 2 - own_pos[0], SCREEN_HEIGHT // 2 - own_pos[1])
    draw_map(surface, global_game_data, camera_offset)