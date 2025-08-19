"""
Do not run this script directly. Instead, call it as a library (e.g. `import socket_server`).
"""

import socket
from socket import socket as Connection
import threading
import time

class Player:
    def __init__(self, conn: Connection, username: str):
        self.conn = conn
        self.username = username

# Standard loopback interface address (localhost).
# 127.0.0.1 makes it so that the server is only accesible from the same machine.
# 0.0.0.0 allows connections from other machines.
HOST = "127.0.0.1"  
PORT = 3000        # Port to listen on (non-privileged ports are > 1023)

BUF_SIZE = 1024

WAITING_TIMEOUT_IN_SECS = 1 

LOCK = threading.Lock()

WAITING_PLAYERS: list[Player] = []


def handle_client(conn: Connection, addr):
    client_deciding_game = True

    while client_deciding_game:
        data = conn.recv(BUF_SIZE).decode()

        if data.startswith("?game"):
            client_deciding_game = False

        else:
            print(f"ERROR: unknown client response: '{data}'")

    fields = data.split(':')
    game = fields[1]
    username = fields[2]

    player = Player(conn, username)

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
    
    time.sleep(WAITING_TIMEOUT_IN_SECS)

    # Logic to start the game
    print("LOG: Two players found. Starting game...")
    start_game(player1, player2)


def start_game(player_1: Player, player_2: Player):
    # Send a message to both players to start the game.
    player_1.conn.sendall(f"?game-start:r:{player_2.username}".encode())
    player_2.conn.sendall(f"?game-start:b:{player_1.username}".encode())


# def start_game(conn_player_1: Connection, conn_player_2: Connection):
#     # Send a message to both players to start the game
#     conn_player_1.sendall(b"?game-start 1")
#     conn_player_2.sendall(b"?game-start 2")
    
#     curr_player_conn = conn_player_1
#     opponent_conn = conn_player_2

#     game_running = True

#     # A simple game loop.
#     while game_running:
#         # Get the move from the player whose turn it is
#         try:
#             curr_player_conn.sendall(b"?turn-info current")
#             opponent_conn.sendall(b"?turn-info opponent")

#             curr_player_command = curr_player_conn.recv(1024).decode()
#             if not curr_player_command:
#                 break # Connection closed

#             if curr_player_command.startswith("?quit"):
#                 print('LOG: game over')
#                 game_running = False
#                 break

#             elif curr_player_command.startswith("?message"):
#                 # Process the move and send the result.
#                 opponent_conn.sendall(f"?curr-player-cmd {curr_player_command}".encode())
            
#             else:
#                 print("ERROR: unknown client command")

#             # Switch turns.
#             curr_player_conn, opponent_conn = opponent_conn, curr_player_conn

#         except Exception:
#             # TODO: Do better error handling.
#             break

#     curr_player_conn.sendall(b"?game-over")
#     opponent_conn.sendall(b"?game-over")


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
            thread.start()