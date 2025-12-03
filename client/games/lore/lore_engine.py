from common_types.game_types import Pair
from common_types.global_state import LoreGlobalState
from games.lore.lore_types import map_pos_to_real_pos, real_pos_to_map_pos, TILE_SIZE, LoreMapTile, LoreResult, ENTITY_WIDTH, LoreMap
import random

class LoreEnemy:
    SPEED = 4 * TILE_SIZE
    # Use a smaller bounding box for detecting wall collisions to avoid having the enemy get stuck.
    ENEMY_WIDTH_FOR_TILES = ENTITY_WIDTH // 3

    def __init__(self, initial_position: Pair):
        # The initial position is adjusted since the enemy processes the position as its center,
        # rather than the top left.
        self.position: tuple[float, float] = (
            initial_position[0] + ENTITY_WIDTH // 2,
            initial_position[1] + ENTITY_WIDTH // 2,
        )
        self.movement: Pair = random.choice([(1, 0), (0, 1)]) # the enemy randomly goes up-down or left-right

    
    def change_direction(self):
        dx, dy = self.movement
        self.movement = (dx * -1, dy * -1)


    def get_new_pos(self, deltatime: float) -> tuple[float, float]:
        x, y = self.position
        dx, dy = self.movement

        return (
            x + dx * LoreEnemy.SPEED * deltatime,
            y + dy * LoreEnemy.SPEED * deltatime,
        )


    def try_move(self, deltatime: float, map: LoreMap):
        new_pos = self.get_new_pos(deltatime)

        corners: list[tuple[float, float]] = [
            (new_pos[0] + LoreEnemy.ENEMY_WIDTH_FOR_TILES, new_pos[1] + LoreEnemy.ENEMY_WIDTH_FOR_TILES),
            (new_pos[0] + LoreEnemy.ENEMY_WIDTH_FOR_TILES, new_pos[1] - LoreEnemy.ENEMY_WIDTH_FOR_TILES),
            (new_pos[0] - LoreEnemy.ENEMY_WIDTH_FOR_TILES, new_pos[1] + LoreEnemy.ENEMY_WIDTH_FOR_TILES),
            (new_pos[0] - LoreEnemy.ENEMY_WIDTH_FOR_TILES, new_pos[1] - LoreEnemy.ENEMY_WIDTH_FOR_TILES),
        ]

        hit_wall = False

        for corner_pos in corners:
            corner_map_pos = real_pos_to_map_pos((int(corner_pos[0]), int(corner_pos[1])))
            tile = map.get_tile_by_map_pos(corner_map_pos)

            if tile is None:
                continue

            if tile == 'wall':
                hit_wall = True
                break

        if hit_wall:
            self.change_direction()
        else:
            self.position = new_pos


    def check_if_should_cause_player_to_die(self, player_position: tuple[float, float]) -> bool:
        px, py = player_position
        ex, ey = self.position

        dist = ((ex - px)**2 + (ey - py)**2)**0.5

        return dist < ENTITY_WIDTH

            
class LoreEngine:
    def __init__(self, client_state: LoreGlobalState):
        self.client_state = client_state
        self.current_kind = self.client_state.kind
        self.result: LoreResult | None = None

        self.enemies: list[LoreEnemy] = [
            LoreEnemy(initial_position=map_pos_to_real_pos(map_pos))
            for map_pos in self.client_state.map.enemy_spawn_map_positions
        ]

    def try_move_player(self, player_movement: Pair, deltatime: float):
        px, py = self.client_state.player_pos
        dx, dy = player_movement

        px += deltatime * dx * self.client_state.player_speed * TILE_SIZE
        py += deltatime * dy * self.client_state.player_speed * TILE_SIZE

        collisions = self.get_tile_collisions((px, py))
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


    def tick(self, player_movement: Pair, deltatime: float):
        self.try_move_player(player_movement, deltatime)

        for enemy in self.enemies:
            enemy.try_move(deltatime, self.client_state.map)

            if enemy.check_if_should_cause_player_to_die(self.client_state.player_pos):
                self.client_state.player_pos = map_pos_to_real_pos(self.client_state.map.player_spawn_map_pos)
                self.client_state.player_lives_left -= 1

                if self.client_state.player_lives_left == 0:
                    self.result = 'failed'
                    return


    def get_tile_collisions(self, new_pos: tuple[float, float]) -> set[LoreMapTile]:
        # Player is drawn from the center.
        corners: list[tuple[float, float]] = [
            (new_pos[0] + ENTITY_WIDTH // 2, new_pos[1] + ENTITY_WIDTH // 2),
            (new_pos[0] + ENTITY_WIDTH // 2, new_pos[1] - ENTITY_WIDTH // 2),
            (new_pos[0] - ENTITY_WIDTH // 2, new_pos[1] + ENTITY_WIDTH // 2),
            (new_pos[0] - ENTITY_WIDTH // 2, new_pos[1] - ENTITY_WIDTH // 2),
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