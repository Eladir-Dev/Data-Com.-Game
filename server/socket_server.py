"""
Do not run this script directly. Instead, call it as a library (e.g. `import socket_server`).
"""

import socket
from socket import socket as Connection
import threading
import time
from typing import Literal

Color = Literal['r', 'b']

class Player:
    def __init__(self, conn: Connection, username: str, starting_deck_repr: str, color: Color | None):
        self.conn = conn
        self.username = username
        self.color = color

        self.starting_deck_repr = starting_deck_repr

# Standard loopback interface address (localhost).
# 127.0.0.1 makes it so that the server is only accesible from the same machine.
# 0.0.0.0 allows connections from other machines.
HOST = "127.0.0.1"  
PORT = 3000        # Port to listen on (non-privileged ports are > 1023)

BUF_SIZE = 1024

WAITING_TIMEOUT_IN_SECS = 1 

LOCK = threading.Lock()

WAITING_PLAYERS: list[Player] = []

#####################
# Move this section to another file.
from typing import Literal

ROWS = 10
COLS = 10

# TODO: Move this over to the `stratego_server` module and import it to this module.
class Game:
    def __init__(self, player1: Player, player2: Player):
        self.board = [[' ' for _ in range(COLS)] for _ in range(ROWS)]
        
        self.is_running = True
        self.turn: Color = 'r'

        self.player1 = player1
        self.player2 = player2
        self.players = [self.player1, self.player2]

        # player color -> Player
        self.turn_map: dict[Color, Player] = { player.color: player for player in self.players } # type: ignore


    def get_current_player(self) -> Player:
        """
        Gets the player that is currently allowed to move.
        """
        return self.turn_map[self.turn]


    def get_board_socket_repr(self) -> str:
        flattened_board = [' ' for _ in range(ROWS * COLS)]

        for r in range(ROWS):
            for c in range(COLS):
                # Maps 2D coords to 1D coords on a flattened array.
                # A flat array is needed to send the board over the socket.
                flat_idx = r * ROWS + c % COLS

                flattened_board[flat_idx] = self.board[r][c]

        return ':'.join(flattened_board)
    

    def run(self):
        """
        Runs the given game in a loop.
        """

        while self.is_running:
            # Send turn info.
            for player in self.players:
                data = f"?turn-info:{self.turn}:{self.get_board_socket_repr()}"
                player.conn.sendall(data.encode())

            # Wait for (valid) player response.
            while True:
                conn_to_process = self.get_current_player().conn
                data = conn_to_process.recv(BUF_SIZE).decode()

                if data.startswith("?move"):
                    fields = data.split(':')
                    from_row = int(fields[1])
                    from_col = int(fields[2])
                    to_row = int(fields[3])
                    to_col = int(fields[4])

                    could_move = self.process_move((from_row, from_col), (to_row, to_col))
                    if could_move:
                        # Break out of the loop if the move was valid and the board was updated.
                        break
                    else:
                        print(f"LOG: ({self.turn}) performed an invalid move")

                else:
                    print(f"ERROR: Invalid response '{data}'")

        # TODO: Send the ?move-result command to the players. 

        # TODO: Figure out how to get the result of the last move 
        # (i.e. if a piece got attacked, which one was defeated, if there was a tie, etc.)
        
        # TODO: Implement the rest of the game here...


    def process_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        """
        Processes the given move. Returns `True` if the move was valid and the board 
        was updated. Otherwise, does nothing and returns `False`.
        """
        # TODO: Actually do this ^^^

        return False

######################

def handle_client(conn: Connection, addr):
    client_deciding_game = True

    while client_deciding_game:
        data = conn.recv(BUF_SIZE).decode()

        if data.startswith("?game"):
            client_deciding_game = False
            print(f"LOG: got data ({data})")

        else:
            print(f"ERROR: unknown client response: '{data}'")

    fields = data.split(':')
    game = fields[1]
    username = fields[2]
    starting_deck_repr = ':'.join(fields[3:])

    # The player's color has not been decided yet.
    player = Player(conn, username, starting_deck_repr, color=None)

    if game == "stratego":
        move_player_to_stratego_queue(player)
    elif game == "wordle":
        print("ERROR: wordle is unimplemented")
    else:
        print(f"ERROR: unknown game '{game}'")


def move_player_to_stratego_queue(player: Player):
    with LOCK:
        WAITING_PLAYERS.append(player)

     # Wait for an opponent to join.
    while len(WAITING_PLAYERS) < 2:
        time.sleep(WAITING_TIMEOUT_IN_SECS) # Wait and check again
    
    # Once a second player joins, start a new game.
    with LOCK:
        player1 = WAITING_PLAYERS.pop()
        player2 = WAITING_PLAYERS.pop()

        # Set player colors.
        player1.color = 'r'
        player2.color = 'b'
    
    time.sleep(WAITING_TIMEOUT_IN_SECS)

    # Logic to start the game
    start_game(player1, player2)


def start_game(player_1: Player, player_2: Player):
    print("LOG: Two players found. Starting game...")

    assert player_1.color, player_2.color

    # Send a message to both players to start the game.
    player_1.conn.sendall(f"?game-start:{player_1.color}:{player_2.username}".encode())
    player_2.conn.sendall(f"?game-start:{player_2.color}:{player_1.username}".encode())

    print(f"LOG: {player_1.username} ({player_1.color}) has deck {player_1.starting_deck_repr}")
    print(f"LOG: {player_2.username} ({player_2.color}) has deck {player_2.starting_deck_repr}")

    # The game for this thread. 
    game = Game(player_1, player_2)

    # Run the game in a loop.
    game.run()


def run():
    # AF_INET: socket family is IPv4
    # SOCK_STREAM: socket type is TCP (lossless)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"LOG: Server listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            # Start a new thread for each client.
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.daemon = True
            thread.start()
