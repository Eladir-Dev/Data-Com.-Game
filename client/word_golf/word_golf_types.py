from dataclasses import dataclass

WORD_LEN = 5
MAX_FEEDBACK_HIST_SIZE = 6

@dataclass
class WordGolfStartingPlayerInfo:
    """
    Starting data for Word Golf from the client.
    """
    username: str

