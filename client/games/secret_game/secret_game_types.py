from dataclasses import dataclass
from pathlib import Path
from typing import Literal

MAP_RESOLUTION = 32
MAP_FOLDER = Path(__file__).parent / "maps"

TurnState = Literal['straight', 'left', 'right']

@dataclass
class SecretGameStartingPlayerInfo:
    username: str


@dataclass
class SecretGamePlayer:
    username: str
    position: tuple[int, int]
    facing_angle: float


class Map:
    def __init__(self, file_name: str):
        self.tiles = _load_map(file_name)



def get_default_map_path() -> str:
    return f"{MAP_FOLDER}/map_01.txt"


def get_map_tile_sprite_name(tile: str) -> str:
    if tile == '#':
        return 'wall.png'
    elif tile == 'L':
        return 'lap_line.png'
    else:
        return 'track.png'
    

def map_pos_to_real_position(map_pos: tuple[int, int]) -> tuple[int, int]:
    return (map_pos[0] * MAP_RESOLUTION, map_pos[1] * MAP_RESOLUTION)


def real_position_to_map_pos(real_position: tuple[int, int]) -> tuple[int, int]:
    return (real_position[0] // MAP_RESOLUTION, real_position[1] // MAP_RESOLUTION)


def _load_map(file_name: str) -> list[list[str]]:
    rows: list[list[str]] = []

    with open(file_name, "r") as f:
        for raw_line in f.readlines():
            line = raw_line.rstrip()
            rows.append(list(line))

    return rows