from dataclasses import dataclass

WORD_LEN = 5
MAX_FEEDBACK_HIST_SIZE = 6

@dataclass
class WordGolfStartingPlayerInfo:
    """
    Starting data for Word Golf from the client.
    """
    username: str


class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    MAGENTA = (255, 0, 255)