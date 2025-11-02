from secret_game.secret_game_types import SecretGamePlayer, Vector, SecretGameResult, assert_str_is_turn_state, MAP_RESOLUTION, DEFAULT_SPEED
from secret_game.map import Map
from server_types import BUF_SIZE
import socket
import time
import math

class SecretGameGame:
    def __init__(self, players: list[SecretGamePlayer], map: Map):
        self.players = players
        self.map = map

        self.is_running = True

        self._last_timestamp = None
        self.deltatime = 0.1

        self.result: SecretGameResult | None = None

        self.command_buffers = ["" for _ in range(len(self.players))]
        self.player_cmds: list[list[str]] = [[] for _ in range(len(self.players))]


    def send_race_countdown_command(self, player: SecretGamePlayer, count_down: int):
        player.conn.send(f"?countdown:{count_down}\\".encode())


    def send_race_start_command(self, player: SecretGamePlayer):
        player.conn.send(f"?race-start\\".encode())


    def calc_deltatime(self):
        now = time.perf_counter()

        # There is no "last timestamp" in the first frame, so we use a default deltatime value of 10^-4 seconds.
        if self._last_timestamp is None:
            self.deltatime = 0.0001

        else:
            self.deltatime = now - self._last_timestamp

        self._last_timestamp = now


    def move_player(self, player: SecretGamePlayer):
        movement = Vector(
            x=math.cos(player.facing_angle) * player.speed * self.deltatime,
            y=math.sin(player.facing_angle) * player.speed * self.deltatime,
        )
        assert player.position
        player.position += movement


    def turn_player(self, player: SecretGamePlayer):
        if player.turn_state == 'straight':
            return

        angular_speed = math.pi / 2 # radians per second
        angle_sign = 1.0 if player.turn_state == 'right' else -1.0

        player.facing_angle += (angular_speed * angle_sign * self.deltatime)
        player.facing_angle %= math.tau


    def check_collision(self, player: SecretGamePlayer):
        assert player.position

        corners = [
            player.position,
            player.position + Vector(x=MAP_RESOLUTION,y=0),
            player.position + Vector(x=0, y=MAP_RESOLUTION),
            player.position + Vector(x=MAP_RESOLUTION, y=MAP_RESOLUTION),
        ]

        for corner_pos in corners:
            corner_map_pos = (int(corner_pos.x / MAP_RESOLUTION), int(corner_pos.y / MAP_RESOLUTION))
            tile = self.map.get_tile(corner_map_pos[0], corner_map_pos[1])

            if tile is None:
                continue

            hit_wall = False

            if tile.kind == 'wall':
                print(f"LOG: Player '{player.username}' hit a wall")
                hit_wall = True

            elif tile.kind == 'line':
                print(f"LOG: Player '{player.username}' crossed a line")

            elif tile.kind == 'lap_check':
                print(f"LOG: Player '{player.username}' crossed a lap checkpoint")

            if hit_wall:
                player.speed = DEFAULT_SPEED / 4
            else:
                player.speed = DEFAULT_SPEED


    def build_pos_cmd_for_player(self, player_idx: int) -> str:
        pos = self.players[player_idx].position
        assert pos
        return f"?pos:{player_idx}:{int(pos.x)}:{int(pos.y)}\\"


    def send_position_commands(self):
        move_cmds = [self.build_pos_cmd_for_player(i) for i in range(len(self.players))]

        for move_cmd in move_cmds:
            for player in self.players:
                player.conn.sendall(move_cmd.encode())


    def build_angle_cmd_for_player(self, player_idx: int) -> str:
        angle = self.players[player_idx].facing_angle
        return f"?angle:{player_idx}:{angle:.4f}\\"


    def send_angle_commands(self):
        move_cmds = [self.build_angle_cmd_for_player(i) for i in range(len(self.players))]

        for move_cmd in move_cmds:
            for player in self.players:
                player.conn.sendall(move_cmd.encode())
    
    
    def run(self):
        """
        Runs the given game.
        """
        try:
            self.run_main_game_loop()

        # End the game if a connection error occurs.
        except ConnectionResetError:
            self.result = SecretGameResult(winner_idx=None, abrupt_end=True)

        # Game ended.
        print("LOG: A Secret Game ended")

        for player in self.players:
            # The result of the game must have been determined already.
            assert self.result

            try:
                # There is a winner.
                if self.result.winner_idx is not None:
                    player.conn.sendall(f"?game-over:secret_game:winner-determined:{self.result.winner_idx}\\".encode())

                # The game abruptly ended before finishing normally.
                elif self.result.abrupt_end:
                    player.conn.sendall("?game-over:secret_game:abrupt-end\\".encode())

                # Since the winner is None, but there wasn't an abrupt end, that means that 
                # there was a tie.
                else:
                    player.conn.sendall("?game-over:secret_game:tie\\".encode())

            # Do not bother trying to send a game over message if the client's socket is disconnected.
            except ConnectionResetError: pass


    def run_main_game_loop(self):
        """
        Runs the main part of the game loop.
        """
        for i in range(3, -1, -1):
            time.sleep(1)

            for player in self.players: 
                self.send_race_countdown_command(player, count_down=i)

        time.sleep(0.5)
        for player in self.players:
            self.send_race_start_command(player)

        while self.is_running:
            self.calc_deltatime()

            self.send_position_commands()
            self.send_angle_commands()

            for player_idx in range(len(self.players)):
                player = self.players[player_idx]
                self.move_player(player)
                self.turn_player(player)
                self.check_collision(player)

                self.handle_player_client_response(player_idx)


    def read_incoming_player_commands(self, player_idx: int):
        try:
            player = self.players[player_idx]
            conn_to_handle = player.conn
            data = conn_to_handle.recv(BUF_SIZE).decode()
            self.command_buffers[player_idx] += data

            while (cmd_end := self.command_buffers[player_idx].find('\\')) != -1:
                client_cmd = self.command_buffers[player_idx][:cmd_end]

                self.command_buffers[player_idx] = self.command_buffers[player_idx][cmd_end+1:] # +1 for skipping past the trailing `\`

                if not client_cmd.startswith('!'):
                    raise Exception(f"received invalid command: {client_cmd}")
                
                if client_cmd.startswith(('!car-turn', )):
                    self.player_cmds[player_idx].append(client_cmd)
                else:
                    print(f"ERROR: received unknown data from client: '{data}'")

        except socket.timeout: pass


    def handle_player_client_response(self, player_idx: int):
        self.read_incoming_player_commands(player_idx)

        for client_cmd in self.player_cmds[player_idx]:
            if client_cmd.startswith("!car-turn"):
                fields = client_cmd.split(':')
                new_turn_state = fields[1]

                self.players[player_idx].turn_state = assert_str_is_turn_state(new_turn_state)
