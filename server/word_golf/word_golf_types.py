from dataclasses import dataclass, field
from typing import Literal
from server_types import Connection
from collections import deque

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

    stashed_words: set[str] = field(default_factory=lambda: set())

    pending_alerts: deque[str] = field(default_factory=lambda: deque())


@dataclass
class WordGolfOccurrence:
    kind: Literal['wrong_guess', 'correct_guess', 'ran_out_of_guesses', 'sending_stashed_word']
    player_idx: int
    stashed_word: str | None = None


@dataclass
class WordGolfGameResult:
    winner_username: str | None
    abrupt_end: bool

