from dataclasses import dataclass
from typing import Literal

TileKind = Literal['wall', 'dead_zone', 'line', 'lap_check_a', 'lap_check_b', 'spawnpoint_p1', 'spawnpoint_p2', 'track']

@dataclass
class Tile:
    map_pos: tuple[int, int]
    kind: TileKind


def parse_tile_kind(ch: str) -> TileKind:
    match ch:
        case '#':
            return 'wall'
        
        case 'X':
            return 'dead_zone'
        
        case 'L':
            return 'line'
        
        case 'A':
            return 'lap_check_a'
        
        case 'B':
            return 'lap_check_b'
        
        case '1':
            return 'spawnpoint_p1'
        
        case '2':
            return 'spawnpoint_p2'
        
        case ' ':
            return 'track'
        
        case unknown:
            raise ValueError(f"could not parse tile kind, got '{unknown}'")