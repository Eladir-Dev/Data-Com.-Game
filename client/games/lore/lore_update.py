import pygame
from pygame.event import Event
from pygame import Surface

from common_types.global_state import LoreGlobalState
from common_types.game_types import Pair, SCREEN_WIDTH, SCREEN_HEIGHT
from games.lore.lore_types import map_pos_to_real_pos, real_pos_to_map_pos, TILE_SIZE, get_tile_sprite_file_path, LoreMapTile, LoreResult, PLAYER_WIDTH, PLAYER_SPRITE_FILE_PATH
from ui.drawing_utils import draw_sprite_on_surface
from ui import sprite_repository
from pathlib import Path
import functools


class LoreEngine:
    def __init__(self, client_state: LoreGlobalState):
        self.client_state = client_state
        self.current_kind = self.client_state.kind
        self.result: LoreResult | None = None


    def tick(self, player_movement: Pair, deltatime: float):
        print(f"DELTATIME: {deltatime}s")

        px, py = self.client_state.player_pos
        dx, dy = player_movement

        px += deltatime * dx * self.client_state.player_speed * TILE_SIZE
        py += deltatime * dy * self.client_state.player_speed * TILE_SIZE

        collisions = self.get_collisions((px, py))
        if self.check_tile_collision(collisions, 'wall'):
            return
        
        elif (
            self.check_tile_collision(collisions, 'secret_game_car') or 
            self.check_tile_collision(collisions, 'secret_dlc_store_coin') or 
            self.check_tile_collision(collisions, 'secret_paint_bucket')
        ):
            self.result = 'finished'
            return

        self.client_state.player_pos = (px, py)


    def get_collisions(self, new_pos: tuple[float, float]) -> set[LoreMapTile]:
        # Player is drawn from the center.
        corners: list[tuple[float, float]] = [
            (new_pos[0] + PLAYER_WIDTH // 2, new_pos[1] + PLAYER_WIDTH // 2),
            (new_pos[0] + PLAYER_WIDTH // 2, new_pos[1] - PLAYER_WIDTH // 2),
            (new_pos[0] - PLAYER_WIDTH // 2, new_pos[1] + PLAYER_WIDTH // 2),
            (new_pos[0] - PLAYER_WIDTH // 2, new_pos[1] - PLAYER_WIDTH // 2),
        ]

        collsions: set[LoreMapTile] = set()

        for corner_pos in corners:
            corner_map_pos = real_pos_to_map_pos((int(corner_pos[0]), int(corner_pos[1])))
            tile = self.client_state.map.get_tile_by_map_pos(corner_map_pos)

            if tile is None:
                continue

            collsions.add(tile)
        
        return collsions
    

    def check_tile_collision(self, collisions: set[LoreMapTile], tile_kind: LoreMapTile) -> bool:
        return tile_kind in collisions


_LORE_ENGINE: LoreEngine | None = None


def get_lore_engine(client_state: LoreGlobalState) -> LoreEngine:
    global _LORE_ENGINE

    if _LORE_ENGINE is None or _LORE_ENGINE.current_kind != client_state.kind:
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


def draw_extra_floor_tile(surface: Surface, ui_scale: float, tile_draw_pos: Pair):
    floor_sprite_path = get_tile_sprite_file_path('floor')
    assert floor_sprite_path, "Lore floor sprite was not found"

    draw_sprite_on_surface(
        surface,
        ui_scale,
        floor_sprite_path,
        tile_draw_pos,
        (TILE_SIZE, TILE_SIZE),
        rect_origin='top_left',
    )


def draw_map(surface: Surface, global_game_data: LoreGlobalState, camera_offset: Pair):
    tiles = global_game_data.map.tiles

    own_map_pos = real_pos_to_map_pos(global_game_data.get_player_pos())

    min_vis_map_x = max(0, own_map_pos[0] - SCREEN_WIDTH // 2 // TILE_SIZE - 1)
    max_vis_map_x = min(len(tiles[0]), own_map_pos[0] + SCREEN_WIDTH // 2 // TILE_SIZE + 1)

    min_vis_map_y = max(0, own_map_pos[1] - SCREEN_HEIGHT // 2 // TILE_SIZE - 1)
    max_vis_map_y = min(len(tiles), own_map_pos[1] + SCREEN_HEIGHT // 2 // TILE_SIZE + 2) # the +2 is intentional

    for x in range(min_vis_map_x, max_vis_map_x):
        for y in range(min_vis_map_y, max_vis_map_y):
            tile = global_game_data.map.get_tile_by_map_pos((x, y))
            if tile is None:
                raise ValueError(f"ERROR: out of bounds map tile at position{(x, y)}")

            tile_sprite_path = get_tile_sprite_file_path(tile)
            if tile_sprite_path is None:
                continue

            tile_real_pos = map_pos_to_real_pos((x, y))
            tile_draw_pos = (tile_real_pos[0] + camera_offset[0], tile_real_pos[1] + camera_offset[1])

            # Draw the floor underneath the unlock tiles. This is only for better visuals.
            if tile == 'secret_game_car' or tile == 'secret_dlc_store_coin' or tile == 'secret_paint_bucket':
                draw_extra_floor_tile(
                    surface, 
                    global_game_data.ui_scale, 
                    tile_draw_pos,
                )

            draw_sprite_on_surface(
                surface,
                global_game_data.ui_scale,
                tile_sprite_path,
                tile_draw_pos,
                (TILE_SIZE, TILE_SIZE),
                rect_origin='top_left',
            )


def draw_player(surface: Surface, global_game_data: LoreGlobalState, camera_offset: Pair):
    player_pos = global_game_data.get_player_pos()

    draw_pos = (
        player_pos[0] + camera_offset[0], 
        # `player_pos` denotes the player's foot position, so we render the sprite slightly above this position.
        player_pos[1] + camera_offset[1],
    )

    draw_sprite_on_surface(
        surface, 
        global_game_data.ui_scale,
        str(PLAYER_SPRITE_FILE_PATH),
        draw_pos,
        (TILE_SIZE, TILE_SIZE),
        rect_origin='center',
    )


def get_player_input() -> Pair:
    keys = pygame.key.get_pressed()

    x_movement = 0
    if keys[pygame.K_a]:
        x_movement -= 1

    if keys[pygame.K_d]:
        x_movement += 1

    y_movement = 0
    if keys[pygame.K_w]:
        y_movement -= 1
    
    if keys[pygame.K_s]:
        y_movement += 1

    return (x_movement, y_movement)


def lore_update(events: list[Event], surface: Surface, global_game_data: LoreGlobalState, deltatime: float) -> LoreResult | None:
    surface.fill((0, 0, 0))

    subtitle = get_lore_window_subtitle(global_game_data)
    pygame.display.set_caption(f"Lore - {subtitle}")

    player_pos = global_game_data.get_player_pos()
    camera_offset: Pair = (SCREEN_WIDTH // 2 - player_pos[0], SCREEN_HEIGHT // 2 - player_pos[1])

    draw_map(surface, global_game_data, camera_offset)
    draw_player(surface, global_game_data, camera_offset)

    movement = get_player_input()

    lore_engine = get_lore_engine(global_game_data)
    lore_engine.tick(movement, deltatime)

    return lore_engine.result
