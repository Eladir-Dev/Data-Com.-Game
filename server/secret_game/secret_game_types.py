from dataclasses import dataclass, field
from server_types import Connection
from typing import Self

DEFAULT_SPEED = 0.25

@dataclass
class Vector:
    x: float
    y: float

    def __add__(self, other: Self) -> Self:
        return type(self)(
            x=self.x + other.x,
            y=self.y + other.y,
        )


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