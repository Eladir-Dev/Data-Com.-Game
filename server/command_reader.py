import socket
from server_types import Connection, BUF_SIZE
from collections import deque

class ClientCommandReader:
    
    def __init__(self, connections: list[Connection], valid_cmd_prefixes: tuple[str, ...]):
        self._connections = connections
        self._valid_cmd_prefixes = valid_cmd_prefixes

        self._command_buffers = ["" for _ in range(len(self._connections))]
        self._player_cmds: list[deque[str]] = [deque() for _ in range(len(self._connections))]


    def _gather_incoming_commands(self, conn_idx: int):
        try:
            conn = self._connections[conn_idx]
            data = conn.recv(BUF_SIZE).decode()
            self._command_buffers[conn_idx] += data

            while (cmd_end := self._command_buffers[conn_idx].find('\\')) != -1:
                client_cmd = self._command_buffers[conn_idx][:cmd_end]

                self._command_buffers[conn_idx] = self._command_buffers[conn_idx][cmd_end+1:] # +1 for skipping past the trailing `\`

                if not client_cmd.startswith('!'):
                    raise Exception(f"received invalid command: {client_cmd}")
                
                if client_cmd.startswith(self._valid_cmd_prefixes):
                    self._player_cmds[conn_idx].appendleft(client_cmd)
                else:
                    print(f"ERROR: received unknown data from client: '{data}'")

        except socket.timeout: pass


    def yield_commands(self, conn_idx: int):
        self._gather_incoming_commands(conn_idx)

        while len(self._player_cmds[conn_idx]) > 0:
            yield self._player_cmds[conn_idx].pop()