from dataclasses import dataclass, field
from server_types import Connection
from typing import Self

MAP_RESOLUTION = 32
DEFAULT_SPEED = 2

@dataclass
class Vector:
    x: float
    y: float

    def __add__(self, other: Self) -> Self:
        return type(self)(
            x=self.x + other.x,
            y=self.y + other.y,
        )

def real_position_from_map_position(map_pos: tuple[int, int]) -> Vector:
    mx, my = map_pos
    return Vector(x=MAP_RESOLUTION * mx, y=MAP_RESOLUTION * my)



@dataclass
class SecretGamePlayer:
    conn: Connection
    username: str
    position: Vector | None

    speed: float = field(default=DEFAULT_SPEED)
    facing_angle: float = 0.0


@dataclass
class SecretGameResult:
    winner_idx: int | None
    abrupt_end: bool