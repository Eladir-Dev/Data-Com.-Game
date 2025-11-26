from typing import Literal
from pathlib import Path
from common_types.game_types import Pair

LoreKind = Literal['secret_game', 'secret_dlc_store', 'secret_paint_game']

LoreMapTile = Literal[
    'player_spawn_pos', 
    'wall', 
    'floor', 
    'void', 
    'secret_game_car', 
    'secret_dlc_store_coin',
    'secret_paint_bucket',
]

MAPS_DIR = Path(__file__).parent / "maps"
TILE_SIZE = 32

def str_to_lore_map_tile(s: str) -> LoreMapTile:
    match s:
        case 'P': return 'player_spawn_pos'
        case '#': return 'wall'
        case '.': return 'floor'
        case '_': return 'void'
        case 'C': return 'secret_game_car'
        case 'S': return 'secret_dlc_store_coin'
        case 'B': return 'secret_paint_bucket'
        case _: raise ValueError(f"unknown map tile string '{s}'")


def map_pos_to_real_pos(map_pos: Pair) -> Pair:
    mx, my = map_pos
    return (mx * TILE_SIZE, my * TILE_SIZE)


def real_pos_to_map_pos(real_pos: Pair) -> Pair:
    x, y = real_pos
    return (x // TILE_SIZE, y // TILE_SIZE)


class LoreMap:
    def __init__(self, lore_kind: LoreKind):
        # Load the map from the file corresponding to the lore kind.
        self.tiles: list[list[LoreMapTile]] = []

        player_spawn_map_pos: Pair | None = None

        file_name = f"{MAPS_DIR}/map_{lore_kind}.txt"

        with open(file_name, "r") as f:
            r = 0
            for raw_line in f.readlines():
                row: list[LoreMapTile] = []
                line = raw_line.rstrip()

                for c in range(len(line)):
                    x, y = c, r
                    tile = str_to_lore_map_tile(line[c])

                    if tile == 'player_spawn_pos':
                        player_spawn_map_pos = (x, y)

                    row.append(tile)

                self.tiles.append(row)
                r += 1

        if player_spawn_map_pos is None:
            raise ValueError("Player spawn position not found")
        
        self.player_spawn_map_pos = player_spawn_map_pos

        # for row in self.tiles:
        #     print("".join([t[0] for t in row]))


    def get_tile_by_map_pos(self, map_pos: Pair) -> LoreMapTile:
        x, y = map_pos
        r, c = y, x
        return self.tiles[r][c]


def get_tile_sprite_file_name(tile: LoreMapTile) -> str | None:
    match tile:
        case 'floor': return 'floor.png'
        case 'player_spawn_pos': return 'floor.png'
        case 'secret_dlc_store_coin': return 'dlc_unlocker.png'
        case 'secret_game_car': return 'secret_racing_game_unlocker.png'
        case 'secret_paint_bucket': return 'paint_game_unlocker.png'
        case 'void': return None
        case 'wall': return 'wall.png'
