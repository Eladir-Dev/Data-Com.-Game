import socket
from common_types.server_types import BUF_SIZE, Connection
from queue import Queue

class ServerCommandReader:
    def __init__(self, server_conn: Connection, valid_cmd_prefixes: tuple[str, ...], server_cmd_queue: Queue[str]):
        self.server_conn = server_conn
        self.valid_cmd_prefixes = valid_cmd_prefixes
        self.server_cmd_queue = server_cmd_queue

        self.buffer = ""


    def read_incoming_commands(self) -> bool:
        """
        This functions streams the client-bound server commands. Returns `False` if the client should stop, otherwise returns `True`.
        """

        try:
            data = self.server_conn.recv(BUF_SIZE).decode()
            self.buffer += data

            while (cmd_end := self.buffer.find('\\')) != -1:
                server_cmd = self.buffer[:cmd_end]

                self.buffer = self.buffer[cmd_end+1:] # +1 for skipping past the trailing `\`

                if not server_cmd.startswith('?'):
                    raise Exception(f"received invalid command: {server_cmd}")
                
                if server_cmd.startswith(self.valid_cmd_prefixes):
                    self.server_cmd_queue.put(server_cmd)

                    if data.startswith("?game-over"):
                        # Return `False` to signify that the client should stop.
                        return False
                else:
                    print(f"ERROR: received unknown data from server: '{data}'")

            return True

        except socket.timeout: return True