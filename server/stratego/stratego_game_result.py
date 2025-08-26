from .stratego_types import StrategoColor

class StrategoGameResult:
    """
    This class represents the result of a Stratego game. It keeps track if there was a winner 
    and if the game ended normally or it abruptly ended.
    """

    def __init__(self, winner: StrategoColor | None, abrupt_end: bool):
        self.winner = winner
        self.abrupt_end = abrupt_end