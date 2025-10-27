from dataclasses import dataclass
from typing import Literal

TileKind = Literal['wall', 'line', 'lap_check', 'spawnpoint_p1', 'spawnpoint_p2', 'track']

@dataclass
class Tile:
    map_pos: tuple[int, int]
    kind: TileKind


def parse_tile_kind(ch: str) -> TileKind:
    match ch:
        case '#':
            return 'wall'
        
        case 'L':
            return 'line'
        
        case 'C':
            return 'lap_check'
        
        case '1':
            return 'spawnpoint_p1'
        
        case '2':
            return 'spawnpoint_p2'
        
        case ' ':
            return 'track'
        
        case unknown:
            raise ValueError(f"could not parse tile kind, got '{unknown}'")