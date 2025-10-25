"""
Do not run this file directly. Instead call it as a library (e.g. `import socket_client`).
"""

import socket
from queue import Queue
from games.stratego.stratego_types import StrategoStartingPlayerInfo
from games.word_golf.word_golf_types import WordGolfStartingPlayerInfo
from games.secret_game.secret_game_types import SecretGameStartingPlayerInfo

PORT = 49300 # The port used by the server

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
                server_host = fields[3]

                if game == "stratego":
                    starting_deck_repr = ':'.join(fields[4:]) # rejoin the deck

                    connect_stratego(server_host, server_command_queue, client_queue, StrategoStartingPlayerInfo(username, starting_deck_repr))

                elif game == "word_golf":
                    connect_word_golf(server_host, server_command_queue, client_queue, WordGolfStartingPlayerInfo(username))

                elif game == "secret_game":
                    connect_secret_game(server_host, server_command_queue, client_queue, SecretGameStartingPlayerInfo(username))

                else:
                    print(f"ERROR: Unknown game: '{game}'")

            else:
                print(f"ERROR: Unknown client message: '{client_msg}'")


def connect_stratego(server_host: str, server_command_queue: Queue[str], client_queue: Queue[str], starting_player_info: StrategoStartingPlayerInfo):
    """
    Connects to the server. Sends commands from the server back 
    through the server command queue. Receives user messages from the client queue.
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_host, PORT))

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


def connect_word_golf(server_host: str, server_command_queue: Queue[str], client_queue: Queue[str], starting_player_info: WordGolfStartingPlayerInfo):
    """
    Connects to the server. Sends commands from the server back 
    through the server command queue. Receives user messages from the client queue.
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_host, PORT))

        # Prevents the socket from blocking the entire client thread when reading.
        s.settimeout(1.0)

        # Tell the server that this client wants to play Word Golf with the given username.
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

                # Forward server commands to the UI.

                if data.startswith("?update"):
                    server_command_queue.put(data)

                elif data.startswith("?feedback-history"):
                    server_command_queue.put(data)

                elif data.startswith("?stashed-words"):
                    server_command_queue.put(data)

                elif data.startswith("?alert"):
                    server_command_queue.put(data)

                elif data.startswith("?game-over"):
                    # Stop the client.
                    client_running = False

                    # Forward the game over command to the UI.
                    server_command_queue.put(data)

                else:
                    print(f"ERROR: received unknown data from server: '{data}'")

            except socket.timeout: pass

            while not client_queue.empty():
                data = client_queue.get()

                if data.startswith("!guess"):
                    print(f"LOG: trying to send guess command: '{data}'")
                    s.sendall(data.encode())

                elif data.startswith("!send-stashed-word"):
                    print(f"LOG: trying to send stashed word command: '{data}'")
                    s.sendall(data.encode())

                else:
                    print(f"ERROR: Unknown client message '{data}'")


def connect_secret_game(
    server_host: str, 
    server_command_queue: Queue[str], 
    client_queue: Queue[str], 
    starting_player_info: SecretGameStartingPlayerInfo,
):
    """
    Connects to the server. Sends commands from the server back 
    through the server command queue. Receives user messages from the client queue.
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server_host, PORT))

        # Prevents the socket from blocking the entire client thread when reading.
        s.settimeout(1.0)

        # Tell the server that this client wants to play the secret game.
        s.sendall(f"?game:secret_game:{starting_player_info.username}".encode())

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

        VALID_COMMAND_PREFIXES = (
            '?countdown',
            '?race-start',
            '?pos',
            '?game-over',
        )
        client_running = True
        buffer = ""

        while client_running:
            try:
                data = s.recv(BUF_SIZE).decode()
                buffer += data

                while (cmd_end := buffer.find('\\')) != -1:
                    server_cmd = buffer[:cmd_end]

                    buffer = buffer[cmd_end+1:] # +1 for skipping past the trailing `\`

                    print(f"LOG: RECEIVED SECRET SERVER COMMAND: {server_cmd}")

                    if not server_cmd.startswith('?'):
                        raise Exception(f"received invalid command: {server_cmd}")
                    
                    if server_cmd.startswith(VALID_COMMAND_PREFIXES):
                        server_command_queue.put(server_cmd)
                    else:
                        print(f"ERROR: received unknown data from server: '{data}'")

            except socket.timeout: pass

            while not client_queue.empty():
                data = client_queue.get()

                print(f"intercepted secret game client-CMD from client {data}")

                # if data.startswith("!guess"):
                #     print(f"LOG: trying to send guess command: '{data}'")
                #     s.sendall(data.encode())

                # elif data.startswith("!send-stashed-word"):
                #     print(f"LOG: trying to send stashed word command: '{data}'")
                #     s.sendall(data.encode())

                # else:
                #     print(f"ERROR: Unknown client message '{data}'")