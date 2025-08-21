from socket import socket as Connection

from .stratego_types import StrategoColor

class StrategoPlayer:
    def __init__(self, conn: Connection, username: str, starting_deck_repr: str, color: StrategoColor | None):
        self.conn = conn
        self.username = username
        self.color = color

        self.starting_deck_repr = starting_deck_repr