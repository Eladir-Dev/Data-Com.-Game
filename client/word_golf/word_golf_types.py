from dataclasses import dataclass

WORD_LEN = 5

@dataclass
class WordGolfStartingPlayerInfo:
    """
    Starting data for Word Golf from the client.
    """
    username: str

