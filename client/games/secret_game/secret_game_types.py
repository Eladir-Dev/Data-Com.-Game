from dataclasses import dataclass

@dataclass
class SecretGameStartingPlayerInfo:
    username: str


@dataclass
class SecretGamePlayer:
    username: str
    position: tuple[int, int]