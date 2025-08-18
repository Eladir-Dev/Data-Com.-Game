"""
Do not run this file directly. Instead call it as a library (e.g. `import client_core`).
"""

import socket
from queue import Queue

# The server's hostname or IP address.
# Since the server is being ran on the same machine, the loopback address is used.
HOST = "127.0.0.1"  
PORT = 3000        # The port used by the server

BUF_SIZE = 1024

# NOTE: None of the command parsing should be done in this module or should be kept at a minimum.

def connect(server_command_queue: Queue[str], client_queue: Queue[str]):
    """
    Connects to the server. Sends commands from the server back 
    through the server command queue. Receives user messages from the client queue.
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        while True:
            data = s.recv(BUF_SIZE).decode()

            if data.startswith("?game-start"):
                role = int(data.split(" ")[1])
                break

        print(f"LOG: successfully connected to a game as player #{role}")
        server_command_queue.put(data)
        
        while True:
            data = s.recv(BUF_SIZE).decode()

            if data == "?game-over":
                server_command_queue.put(data)
                break

            if not data.startswith("?turn-info"):
                print("ERROR: unknown server response")
                server_command_queue.put(data)
                return

            server_command_queue.put(data)
            turn_info = data.split(" ")[1]

            if turn_info == "current":
                # Get a message from the UI.
                print("LOG: waiting for data from UI")
                msg = client_queue.get()

                if msg in {'quit', 'exit'}:
                    s.sendall(b"?quit")
                else:
                    s.sendall(f"?message {msg}".encode())
                
            else:
                data = s.recv(BUF_SIZE).decode()
                if not data.startswith("?curr-player-cmd"):
                    print('ERROR: unknown server command')
                    server_command_queue.put(data)
                    return
                
                cmd_by_curr_player = " ".join(data.split(" ")[1:])
                server_command_queue.put(cmd_by_curr_player)
                print(F"LOG: The current player performed this command: {cmd_by_curr_player}")

        # Game ended.
        print("LOG: game ended")


# DEPRECATED DO NOT USE.
def connect_as_debug_chat():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        while True:
            data = s.recv(BUF_SIZE).decode()

            if data.startswith("?game-start"):
                role = int(data.split(" ")[1])
                break

        print(f"LOG: successfully connected to a game as player #{role}")
        
        while True:
            data = s.recv(BUF_SIZE).decode()

            if data == "?game-over":
                break

            if not data.startswith("?turn-info"):
                print("ERROR: unknown server response")
                return

            turn_info = data.split(" ")[1]

            if turn_info == "current":
                msg = None

                while msg is None:
                    user_input = input("> ")
                    if ' ' not in user_input:
                        msg = user_input
                    else:
                        print("ERROR: message cannot contain spaces for testing purposes")

                if msg in {'quit', 'exit'}:
                    s.sendall(b"?quit")
                else:
                    s.sendall(f"?message {msg}".encode())
                
            else:
                data = s.recv(BUF_SIZE).decode()
                if not data.startswith("?curr-player-cmd"):
                    print('ERROR: unknown server command')
                    return
                
                cmd_by_curr_player = " ".join(data.split(" ")[1:])
                print(F"LOG: The current player performed this command: {cmd_by_curr_player}")

        # Game ended.
        print("LOG: game ended")