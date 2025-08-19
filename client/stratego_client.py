"""
Aque se encuentra la logica de stratego
"""
# El cliente (jugador) va a tener listo su deck antes de empezar el juego

# recoger queue 
# leer los decks
# prepara el tablero
# recoger comando
# empezar partida (el rojo empieza)



# [0R][SR][FR][1R][9R]
# [0R][SR][FR][1R][9R]

ROWS = 10
COLS = 10

DECK_ROWS = 4

class PlayerInfo:
    def __init__(self, username: str, starting_deck_str_repr: str):
        self.username = username
        self.starting_deck_repr = starting_deck_str_repr


class Board:
    def __init__(self):
        self.elements = [' ' for _ in range(ROWS * COLS)]

    
    def to_socket_msg_repr(self) -> str:
        return _flat_array_to_message_repr(self.elements)


def temp_generate_placeholder_deck() -> list[str]:
    deck = ['0' for _ in range(DECK_ROWS * COLS)]
    return deck


def deck_to_socket_message_repr(deck: list[str]):
    return _flat_array_to_message_repr(deck)


def _flat_array_to_message_repr(flat_array: list[str] ) -> str:
    return ':'.join(flat_array)

