import pygame
from pygame.event import Event
from pygame import Surface

from common_types.global_state import LoreGlobalState
from common_types.game_types import Pair, SCREEN_WIDTH, SCREEN_HEIGHT
from games.lore.lore_types import map_pos_to_real_pos, real_pos_to_map_pos, TILE_SIZE, get_tile_sprite_file_name
from ui.drawing_utils import draw_sprite_on_surface
from pathlib import Path

SPRITE_FOLDER = Path(__file__).parent / "assets"


import time

class LoreEngine:
    def __init__(self, client_state: LoreGlobalState):
        self.client_state = client_state
        self.deltatime = 0.1
        self._last_timestamp: float | None = None


    def calc_deltatime(self):
        if self._last_timestamp is None:
            self.deltatime = 0.1
            self._last_timestamp = time.perf_counter()

        else:
            now = time.perf_counter()
            self.deltatime = now - self._last_timestamp
            self._last_timestamp = now


    def tick(self):
        pass

        # time.sleep(0.5)


_LORE_ENGINE: LoreEngine | None = None


def get_lore_engine(client_state: LoreGlobalState) -> LoreEngine:
    global _LORE_ENGINE

    if _LORE_ENGINE is None:
        _LORE_ENGINE = LoreEngine(client_state)

    return _LORE_ENGINE


def get_lore_window_subtitle(global_game_data: LoreGlobalState):
    if global_game_data.kind == 'secret_game':
        return "Garage"

    elif global_game_data.kind == 'secret_dlc_store':
        return "Store"

    elif global_game_data.kind == 'secret_paint_game':
        return "Paint Shop"

    else:
        return "Unknown" # unreachable


def draw_map(surface: Surface, global_game_data: LoreGlobalState, camera_offset: Pair):
    tiles = global_game_data.map.tiles

    own_map_pos = real_pos_to_map_pos(global_game_data.player_pos)

    min_vis_map_x = max(0, own_map_pos[0] - SCREEN_WIDTH // 2 // TILE_SIZE - 1)
    max_vis_map_x = min(len(tiles[0]), own_map_pos[0] + SCREEN_WIDTH // 2 // TILE_SIZE + 1)

    min_vis_map_y = max(0, own_map_pos[1] - SCREEN_HEIGHT // 2 // TILE_SIZE - 1)
    max_vis_map_y = min(len(tiles), own_map_pos[1] + SCREEN_HEIGHT // 2 // TILE_SIZE + 2) # the +2 is intentional

    # print(min_vis_map_x, max_vis_map_x, min_vis_map_y, max_vis_map_y)
    # print(f"REAL DIM: {len(global_game_data.map.tiles[0])}, {len(global_game_data.map.tiles)}")

    for x in range(min_vis_map_x, max_vis_map_x):
        for y in range(min_vis_map_y, max_vis_map_y):
            tile = global_game_data.map.get_tile_by_map_pos((x, y))

            tile_sprite_file_name = get_tile_sprite_file_name(tile)
            if tile_sprite_file_name is None:
                continue

            tile_sprite = pygame.image.load(f"{SPRITE_FOLDER}/{tile_sprite_file_name}")

            real_pos = map_pos_to_real_pos((x, y))

            draw_sprite_on_surface(
                surface,
                global_game_data.ui_scale,
                tile_sprite,
                (real_pos[0] + camera_offset[0], real_pos[1] + camera_offset[1]),
                (TILE_SIZE, TILE_SIZE),
                rect_origin='top_left',
            )


def draw_player(surface: Surface, global_game_data: LoreGlobalState, camera_offset: Pair):
    draw_pos = (
        global_game_data.player_pos[0] + camera_offset[0], 
        # `player_pos` denotes the player's foot position, so we render the sprite slightly above this position.
        global_game_data.player_pos[1] + camera_offset[1] - TILE_SIZE,
    )
    player_sprite = pygame.image.load(f"{SPRITE_FOLDER}/player.png")

    draw_sprite_on_surface(
        surface, 
        global_game_data.ui_scale,
        player_sprite,
        draw_pos,
        (TILE_SIZE, TILE_SIZE),
        rect_origin='center',
    )


def lore_update(events: list[Event], surface: Surface, global_game_data: LoreGlobalState) -> str | None:
    surface.fill((0, 0, 0))

    subtitle = get_lore_window_subtitle(global_game_data)
    pygame.display.set_caption(f"Lore - {subtitle} - {global_game_data.player_pos}")

    lore_engine = get_lore_engine(global_game_data)
    lore_engine.tick()

    player_pos = global_game_data.player_pos
    camera_offset = (SCREEN_WIDTH // 2 - player_pos[0], SCREEN_HEIGHT // 2 - player_pos[1])

    draw_map(surface, global_game_data, camera_offset)
    draw_player(surface, global_game_data, camera_offset)

    # TODO: actually add the lore
