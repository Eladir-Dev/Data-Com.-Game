from dataclasses import dataclass, field
import math
from server_types import Connection
from typing import Self, Literal

MAP_RESOLUTION = 32
DEFAULT_SPEED = 10 * MAP_RESOLUTION

TURN_SPEED = math.pi # radians per second

TurnState = Literal['straight', 'left', 'right']

def assert_str_is_turn_state(s: str) -> TurnState:
    if s not in {'straight', 'left', 'right'}:
        raise ValueError(f"invalid turn state '{s}'")
    
    return s # type: ignore


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
    turn_state: TurnState = 'straight'

    completed_laps = 0
    lap_state: Literal['initial', 'looking_for_line', 'looking_for_checkpoint_a', 'looking_for_checkpoint_b'] = 'initial' 


@dataclass
class SecretGameResult:
    winner_idx: int | None
    abrupt_end: bool