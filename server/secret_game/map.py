from secret_game.tile import Tile, parse_tile_kind
from secret_game.secret_game_types import real_position_from_map_position

class Map:
    def __init__(self, file_name: str):
        self.read_map_data(file_name)


    def read_map_data(self, file_name: str):
        self.grid: list[list[Tile]] = []
        p1_spawn_map_pos = None
        p2_spawn_map_pos = None

        with open(file_name, 'r') as f:
            r = 0

            for raw_line in f.readlines():
                line = raw_line.rstrip()
                row = []

                for c in range(len(line)):
                    x, y = c, r

                    kind = parse_tile_kind(line[c])

                    if kind == 'spawnpoint_p1':
                        p1_spawn_map_pos = (x, y)

                    elif kind == 'spawnpoint_p2':
                        p2_spawn_map_pos = (x, y)

                    row.append(Tile(map_pos=(x, y), kind=kind))

                self.grid.append(row)
                r += 1

        assert p1_spawn_map_pos, "No P1 spawn position found in map"
        assert p2_spawn_map_pos, "No P2 spawn position found in map"

        self.p1_spawn_map_pos = real_position_from_map_position(p1_spawn_map_pos)
        self.p2_spawn_map_pos = real_position_from_map_position(p2_spawn_map_pos)
        
    
    def get_tile(self, map_x: int, max_y: int) -> Tile | None:
        if map_x >= 0 and map_x < len(self.grid[0]) and max_y >= 0 and max_y < len(self.grid):
            r, c = max_y, map_x
            return self.grid[r][c]
        else:
            return None