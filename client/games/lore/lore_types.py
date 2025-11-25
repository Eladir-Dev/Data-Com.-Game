from typing import Literal
from pathlib import Path

LoreKind = Literal['secret_game', 'secret_dlc_store', 'secret_paint_game']

MAPS_DIR = Path(__file__).parent / "maps"

class LoreMap:
    def __init__(self, lore_kind: LoreKind):
        # Load the map from the file corresponding to the lore kind.
        self.tiles = []
        file_name = f"{MAPS_DIR}/{lore_kind}.txt"

        with open(file_name, "r") as f:
            for raw_line in f.readlines():
                line = raw_line.rstrip()
                self.tiles.append(list(line))

