"""
Do not run this file directly. Instead call it as a library (e.g. `import client`).
"""

import socket

# The server's hostname or IP address.
# Since the server is being ran on the same machine, the loopback address is used.
HOST = "127.0.0.1"  
PORT = 3000        # The port used by the server

BUF_SIZE = 1024

def connect():
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