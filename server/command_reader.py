import socket
from server_types import Connection, BUF_SIZE

class CommandReader:
    
    def __init__(self, connections: list[Connection], valid_cmd_prefixes: tuple[str]):
        self.connections = connections
        self.valid_cmd_prefixes = valid_cmd_prefixes

        self.command_buffers = ["" for _ in range(len(self.connections))]
        self.player_cmds: list[list[str]] = [[] for _ in range(len(self.connections))]


    def read_incoming_commands(self, conn_idx: int):
        try:
            conn = self.connections[conn_idx]
            data = conn.recv(BUF_SIZE).decode()
            self.command_buffers[conn_idx] += data

            while (cmd_end := self.command_buffers[conn_idx].find('\\')) != -1:
                client_cmd = self.command_buffers[conn_idx][:cmd_end]

                self.command_buffers[conn_idx] = self.command_buffers[conn_idx][cmd_end+1:] # +1 for skipping past the trailing `\`

                if not client_cmd.startswith('!'):
                    raise Exception(f"received invalid command: {client_cmd}")
                
                if client_cmd.startswith(self.valid_cmd_prefixes):
                    self.player_cmds[conn_idx].append(client_cmd)
                else:
                    print(f"ERROR: received unknown data from client: '{data}'")

        except socket.timeout: pass
