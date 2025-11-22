from pygame.event import Event
from pygame import Surface
from common_types.global_state import SecretGameGlobalState
import pygame
from pathlib import Path
from ui.drawing_utils import draw_sprite_on_surface, draw_text
from common_types.game_types import SCREEN_WIDTH, SCREEN_HEIGHT, Pair
from games.secret_game.secret_game_types import get_map_tile_sprite_name, map_pos_to_real_position, real_position_to_map_pos, MAP_RESOLUTION, TurnState
import math

SPITE_FOLDER = Path(__file__).parent / "assets"

def draw_map(surface: Surface, global_game_data: SecretGameGlobalState, camera_offset: Pair):
    tiles = global_game_data.map.tiles

    own_map_pos = real_position_to_map_pos(global_game_data.get_own_data().position)

    min_vis_map_x = max(0, own_map_pos[0] - SCREEN_WIDTH // 2 // MAP_RESOLUTION - 1)
    max_vis_map_x = min(len(tiles[0]), own_map_pos[0] + SCREEN_WIDTH // 2 // MAP_RESOLUTION + 1)

    min_vis_map_y = max(0, own_map_pos[1] - SCREEN_HEIGHT // 2 // MAP_RESOLUTION - 1)
    max_vis_map_y = min(len(tiles), own_map_pos[1] + SCREEN_HEIGHT // 2 // MAP_RESOLUTION + 1)

    for x in range(min_vis_map_x, max_vis_map_x):
        for y in range(min_vis_map_y, max_vis_map_y):
            r, c = y, x
            tile_sprite = pygame.image.load(f"{SPITE_FOLDER}/{get_map_tile_sprite_name(tiles[r][c])}")

            real_pos = map_pos_to_real_position((x, y))

            draw_sprite_on_surface(
                surface,
                tile_sprite,
                (real_pos[0] + camera_offset[0], real_pos[1] + camera_offset[1]),
                (MAP_RESOLUTION, MAP_RESOLUTION),
                rect_origin='top_left',
            )


def draw_players(surface: Surface, global_game_data: SecretGameGlobalState, camera_offset: Pair):
    p1 = global_game_data.players[0]
    p2 = global_game_data.players[1]

    p1_angle_deg = -(p1.facing_angle * 180 / math.pi)
    p2_angle_deg = -(p2.facing_angle * 180 / math.pi)

    p1_sprite = pygame.transform.rotate(pygame.image.load(f"{SPITE_FOLDER}/player_01.png"), p1_angle_deg)
    p2_sprite = pygame.transform.rotate(pygame.image.load(f"{SPITE_FOLDER}/player_02.png"), p2_angle_deg)

    p1_draw_location = (p1.position[0] + camera_offset[0] + MAP_RESOLUTION // 2, p1.position[1] + camera_offset[1] + MAP_RESOLUTION // 2)
    p2_draw_location = (p2.position[0] + camera_offset[0] + MAP_RESOLUTION // 2, p2.position[1] + camera_offset[1] + MAP_RESOLUTION // 2)

    draw_sprite_on_surface(
        surface,
        p1_sprite,
        location=p1_draw_location,
    )

    draw_sprite_on_surface(
        surface,
        p2_sprite,
        location=p2_draw_location,
    )

    draw_player_nametags(surface, global_game_data, [p1_draw_location, p2_draw_location])


def draw_player_nametags(surface: Surface, global_game_data: SecretGameGlobalState, player_draw_locations: list[Pair]):
    COLORS = [
        (100, 100, 255), # player 1
        (255, 100, 100), # player 2
    ]

    for player_idx in range(len(global_game_data.players)):
        draw_text(
            surface,
            text=global_game_data.players[player_idx].username,
            font_size=MAP_RESOLUTION * 2 // 3,
            location=(player_draw_locations[player_idx][0], player_draw_locations[player_idx][1] - MAP_RESOLUTION),
            color=COLORS[player_idx],
        )


def gen_move_command(new_turn_state: TurnState) -> str:
    return f"!car-turn:{new_turn_state}\\"


def handle_turning(global_game_data: SecretGameGlobalState) -> str | None:
    keys = pygame.key.get_pressed()

    should_go_straight = (keys[pygame.K_a] and keys[pygame.K_d]) or (not keys[pygame.K_a] and not keys[pygame.K_d])
    turn_state_changed = False

    if should_go_straight and global_game_data.turn_state != 'straight':
        global_game_data.turn_state = 'straight'
        turn_state_changed = True

    elif keys[pygame.K_a] and global_game_data.turn_state != 'left':
        global_game_data.turn_state = 'left'
        turn_state_changed = True

    elif keys[pygame.K_d] and global_game_data.turn_state != 'right':
        global_game_data.turn_state = 'right'
        turn_state_changed = True

    if turn_state_changed:
        return gen_move_command(global_game_data.turn_state)


def secret_game_update(events: list[Event], surface: Surface, global_game_data: SecretGameGlobalState) -> str | None:
    surface.fill((0, 0, 0))

    debug_string = f"{global_game_data.get_own_data().username} ({global_game_data.get_own_data().position}) facing {global_game_data.get_own_data().facing_angle} (LAPS: {global_game_data.get_own_data().completed_laps} / 3) " + \
        f"VS {global_game_data.get_opp_data().username} ({global_game_data.get_opp_data().position}) facing {global_game_data.get_opp_data().facing_angle} (LAPS: {global_game_data.get_opp_data().completed_laps} / 3)"

    pygame.display.set_caption(debug_string)

    own_pos = global_game_data.get_own_data().position
    camera_offset = (SCREEN_WIDTH // 2 - own_pos[0], SCREEN_HEIGHT // 2 - own_pos[1])

    draw_map(surface, global_game_data, camera_offset)
    draw_players(surface, global_game_data, camera_offset)

    car_turn_cmd = handle_turning(global_game_data)
    
    return car_turn_cmd