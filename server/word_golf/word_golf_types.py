from dataclasses import dataclass, field
from server_types import Connection

@dataclass
class WordGolfPlayer:
    conn: Connection
    username: str

    points: int = 0
    # The default factory is to avoid the issues that Python has with mutable 
    # default arguments.
    queued_words: list[str] = field(default_factory=lambda: [])

    already_guessed_words: set[str] = field(default_factory=lambda: set())

    feedback_history: list[str] = field(default_factory=lambda: [])

