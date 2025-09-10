"""
Do not run this script directly. Instead, call it as a library (e.g. `import socket_server`).
"""

import socket
import threading
import time

from server_types import Connection, BUF_SIZE
from stratego.stratego_game import StrategoGame
from stratego.stratego_player import StrategoPlayer

from word_golf.word_golf_types import WordGolfPlayer
from word_golf.word_golf_game import WordGolfGame

# Standard loopback interface address (localhost).
# 127.0.0.1 makes it so that the server is only accesible from the same machine.
# 0.0.0.0 allows connections from other machines.
HOST = "0.0.0.0"  
PORT = 49300        # Port to listen on (non-privileged ports are > 1023)

WAITING_TIMEOUT_IN_SECS = 1 

LOCK = threading.Lock()

WAITING_STRATEGO_PLAYERS: list[StrategoPlayer] = []

WAITING_WORD_GOLF_PLAYERS: list[WordGolfPlayer] = []

def handle_client(conn: Connection, addr):
    # This timeout is for communicating with existing clients.
    conn.settimeout(0.1)
    client_deciding_game = True

    while client_deciding_game:
        try:
            data = conn.recv(BUF_SIZE).decode()

            if data.startswith("?game"):
                client_deciding_game = False
                print(f"LOG: got data ({data})")

            else:
                print(f"ERROR: unknown client response: '{data}'")

        except socket.timeout: continue

    fields = data.split(':')
    game = fields[1]
    username = fields[2]
    
    if game == "stratego":
        starting_deck_repr = ':'.join(fields[3:])
        # The player's color has not been decided yet.
        stratego_player = StrategoPlayer(conn, username, starting_deck_repr, color=None)

        move_player_to_stratego_queue(stratego_player)

    elif game == "word_golf":
        word_golf_player = WordGolfPlayer(conn, username)

        move_player_to_word_golf_queue(word_golf_player)

    else:
        print(f"ERROR: unknown game '{game}'")


def move_player_to_stratego_queue(player: StrategoPlayer):
    with LOCK:
        WAITING_STRATEGO_PLAYERS.append(player)

     # Wait for an opponent to join.
    while len(WAITING_STRATEGO_PLAYERS) < 2:
        time.sleep(WAITING_TIMEOUT_IN_SECS) # Wait and check again
    
    # Once a second player joins, start a new game.
    with LOCK:
        player1 = WAITING_STRATEGO_PLAYERS.pop()
        player2 = WAITING_STRATEGO_PLAYERS.pop()

        # Set player colors.
        player1.color = 'r'
        player2.color = 'b'
    
    time.sleep(WAITING_TIMEOUT_IN_SECS)

    # Logic to start the game
    start_stratego_game(player1, player2)


def move_player_to_word_golf_queue(player: WordGolfPlayer):
    with LOCK:
        WAITING_WORD_GOLF_PLAYERS.append(player)

     # Wait for an opponent to join.
    while len(WAITING_WORD_GOLF_PLAYERS) < 2:
        time.sleep(WAITING_TIMEOUT_IN_SECS) # Wait and check again
    
    # Once a second player joins, start a new game.
    with LOCK:
        player1 = WAITING_WORD_GOLF_PLAYERS.pop()
        player2 = WAITING_WORD_GOLF_PLAYERS.pop()

    
    time.sleep(WAITING_TIMEOUT_IN_SECS)

    # Logic to start the game
    start_word_golf_game(player1, player2)


def start_stratego_game(player_1: StrategoPlayer, player_2: StrategoPlayer):
    print("LOG: Two players found. Starting Stratego game...")

    assert player_1.color, player_2.color

    # Send a message to both players to start the game.
    player_1.conn.sendall(f"?game-start:stratego:{player_1.color}:{player_2.username}".encode())
    player_2.conn.sendall(f"?game-start:stratego:{player_2.color}:{player_1.username}".encode())

    print(f"LOG: {player_1.username} ({player_1.color}) has deck {player_1.starting_deck_repr}")
    print(f"LOG: {player_2.username} ({player_2.color}) has deck {player_2.starting_deck_repr}")

    # The game for this thread. 
    game = StrategoGame(player_1, player_2)

    # Run the game in a loop.
    game.run()


def start_word_golf_game(player_1: WordGolfPlayer, player_2: WordGolfPlayer):
    print("LOG: Two players found. Starting Word Golf game...")

    # Send a message to both players to start the game.
    player_1.conn.sendall(f"?game-start:word_golf:{player_2.username}".encode())
    player_2.conn.sendall(f"?game-start:word_golf:{player_1.username}".encode())

    # Give the clients time to process the game's start.
    time.sleep(0.5)

    print(f"LOG: {player_1.username} joined a Word golf game")
    print(f"LOG: {player_2.username} joined a Word golf game")

    # The game for this thread. 
    game = WordGolfGame([player_1, player_2])

    # Run the game in a loop.
    game.run()


def run():
    # AF_INET: socket family is IPv4
    # SOCK_STREAM: socket type is TCP (lossless)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        # This timeout is only for the accept calls (for connecting new clients).
        s.settimeout(2.0)
        print(f"LOG: Server listening on {HOST}:{PORT}")

        while True:
            try:
                conn, addr = s.accept()
                # Start a new thread for each client.
                thread = threading.Thread(target=handle_client, args=(conn, addr))
                thread.daemon = True
                thread.start()

            except socket.timeout: continue
