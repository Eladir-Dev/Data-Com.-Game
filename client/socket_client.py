"""
Do not run this file directly. Instead call it as a library (e.g. `import socket_client`).
"""

import socket
from queue import Queue
from stratego_client import PlayerInfo

# The server's hostname or IP address.
# Since the server is being ran on the same machine, the loopback address is used.
HOST = "127.0.0.1"  
PORT = 3000        # The port used by the server

BUF_SIZE = 1024

GLOBALS: dict[str, PlayerInfo | None] = {
    "player_info": None,
}

def connect(server_command_queue: Queue[str], client_queue: Queue[str]):
    while True:
        
        # Wait for the client to decide to play.
        while not client_queue.empty():
            client_msg = client_queue.get()

            if client_msg.startswith("!want-play-game"):
                fields = client_msg.split(':')
                game = fields[1]
                username = fields[2]
                starting_deck_repr = ':'.join(fields[3:]) # rejoin the deck

                GLOBALS["player_info"] = PlayerInfo(username, starting_deck_repr)

                if game == "stratego":
                    connect_stratego(server_command_queue, client_queue)
                    # Should there be a break here?

                elif game == "wordle":
                    print("ERROR: wordle is not implemented")

                else:
                    print(f"ERROR: Unknown game: '{game}'")

            else:
                print(f"ERROR: Unknown client message: '{client_msg}'")


def connect_stratego(server_command_queue: Queue[str], client_queue: Queue[str]):
    """
    Connects to the server. Sends commands from the server back 
    through the server command queue. Receives user messages from the client queue.
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        player_info = GLOBALS['player_info']
        # This variable must have been initialized by this point.
        assert player_info

        # Tell the server that this client wants to play Stratego under the given username and starting deck.
        s.sendall(f"?game:stratego:{player_info.username}:{player_info.starting_deck_repr}".encode())

        # Wait for the server to confirm that the game has started.
        while True:
            data = s.recv(BUF_SIZE).decode()

            if data.startswith("?game-start"):
                fields = data.split(':')
                color = fields[1]
                opponent_name = fields[2]

                # TODO: use these fields, send them to the UI.
                print(f"COLOR: {color}")
                print(f"OPPONENT NAME: {opponent_name}")
                break

            else:
                print(f"ERROR: Unknown server response: '{data}'")

        # TODO: implement game...
        print("LOG: starting game on client...")

