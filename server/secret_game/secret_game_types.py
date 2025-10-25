from dataclasses import dataclass, field
from server_types import Connection
from typing import Self, Literal

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

    position: Vector = field(default_factory=lambda: Vector(x=0, y=0))
    speed: float = 2.0
    facing_angle: float = 0.0


@dataclass
class SecretGameResult:
    winner_idx: int | None
    abrupt_end: bool