"""
Do not run this file directly. Instead call it as a library (e.g. `import socket_client`).
"""

import socket
from queue import Queue
from stratego.stratego_types import StrategoStartingPlayerInfo
from word_golf.word_golf_types import WordGolfStartingPlayerInfo

# The server's hostname or IP address.
# Since the server is being ran on the same machine, the loopback address is used.
HOST = "127.0.0.1"  
PORT = 3000        # The port used by the server

BUF_SIZE = 1024

def connect(server_command_queue: Queue[str], client_queue: Queue[str]):
    while True:
        
        # Wait for the client to decide to play.
        while not client_queue.empty():
            client_msg = client_queue.get()

            if client_msg.startswith("!want-play-game"):
                fields = client_msg.split(':')
                game = fields[1]
                username = fields[2]

                if game == "stratego":
                    starting_deck_repr = ':'.join(fields[3:]) # rejoin the deck

                    connect_stratego(server_command_queue, client_queue, StrategoStartingPlayerInfo(username, starting_deck_repr))
                    # Should there be a break here?

                elif game == "word_golf":
                    connect_word_golf(server_command_queue, client_queue, WordGolfStartingPlayerInfo(username))
                    # Should there be a break here?

                else:
                    print(f"ERROR: Unknown game: '{game}'")

            else:
                print(f"ERROR: Unknown client message: '{client_msg}'")


def connect_stratego(server_command_queue: Queue[str], client_queue: Queue[str], starting_player_info: StrategoStartingPlayerInfo):
    """
    Connects to the server. Sends commands from the server back 
    through the server command queue. Receives user messages from the client queue.
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # Prevents the socket from blocking the entire client thread when reading.
        s.settimeout(1.0)

        # Tell the server that this client wants to play Stratego under the given username and starting deck.
        s.sendall(f"?game:stratego:{starting_player_info.username}:{starting_player_info.starting_deck_repr}".encode())

        # Wait for the server to confirm that the game has started.
        while True:
            try:
                data = s.recv(BUF_SIZE).decode()

                if data.startswith("?game-start"):
                    # Forward the game start command to the UI.
                    server_command_queue.put(data)
                    break

                else:
                    print(f"ERROR: Unknown server response: '{data}'")

            except socket.timeout: pass

        print("LOG: starting Stratego game on client...")

        client_running = True

        while client_running:
            try:
                data = s.recv(BUF_SIZE).decode()

                # Forward the turn info server command to the UI.
                if data.startswith("?turn-info"):
                    server_command_queue.put(data)

                # Forward move result commands to the UI.
                elif data.startswith("?move-result"):
                    server_command_queue.put(data)

                elif data.startswith("?game-over"):
                    # Stop the client.
                    client_running = False

                    # Forward the game over command to the UI.
                    server_command_queue.put(data)

                else:
                    print(f"CLIENT ERROR: Unknown server command '{data}'")

            except socket.timeout: pass

            while not client_queue.empty():
                data = client_queue.get()

                # Forward the move command to the server.
                if data.startswith('!move'):
                    print(f"LOG: trying to send move command: '{data}'")
                    s.sendall(data.encode())

                else:
                    print(f"ERROR: Unknown client message '{data}'")


def connect_word_golf(server_command_queue: Queue[str], client_queue: Queue[str], starting_player_info: WordGolfStartingPlayerInfo):
    """
    Connects to the server. Sends commands from the server back 
    through the server command queue. Receives user messages from the client queue.
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        # Prevents the socket from blocking the entire client thread when reading.
        s.settimeout(1.0)

        # Tell the server that this client wants to play Stratego under the given username and starting deck.
        s.sendall(f"?game:word_golf:{starting_player_info.username}".encode())

        # Wait for the server to confirm that the game has started.
        while True:
            try:
                data = s.recv(BUF_SIZE).decode()

                if data.startswith("?game-start"):
                    # Forward the game start command to the UI.
                    server_command_queue.put(data)
                    break

                else:
                    print(f"ERROR: Unknown server response: '{data}'")

            except socket.timeout: pass

        print("LOG: starting Word Golf game on client...")

        client_running = True

        while client_running:
            try:
                data = s.recv(BUF_SIZE).decode()
                print(f"ERROR: received data from server: '{data}'")

                # # Forward the turn info server command to the UI.
                # if data.startswith("?turn-info"):
                #     server_command_queue.put(data)

                # # Forward move result commands to the UI.
                # elif data.startswith("?move-result"):
                #     server_command_queue.put(data)

                # elif data.startswith("?game-over"):
                #     # Stop the client.
                #     client_running = False

                #     # Forward the game over command to the UI.
                #     server_command_queue.put(data)

                # else:
                    # print(f"CLIENT ERROR: Unknown server command '{data}'")

            except socket.timeout: pass

            while not client_queue.empty():
                data = client_queue.get()
                print(f"ERROR: received data from server: '{data}'")

                # # Forward the move command to the server.
                # if data.startswith('!move'):
                #     print(f"LOG: trying to send move command: '{data}'")
                #     s.sendall(data.encode())

                # else:
                #     print(f"ERROR: Unknown client message '{data}'")