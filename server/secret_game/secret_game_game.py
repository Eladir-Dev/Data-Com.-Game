from secret_game.secret_game_types import SecretGamePlayer, Vector, SecretGameResult, TurnState, assert_str_is_turn_state
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


    def send_race_countdown_command(self, player: SecretGamePlayer, count_down: int):
        player.conn.send(f"?countdown:{count_down}\\".encode())


    def send_race_start_command(self, player: SecretGamePlayer):
        player.conn.send(f"?race-start\\".encode())


    def calc_deltatime(self):
        now = time.perf_counter()

        if self._last_timestamp is not None:
            self.deltatime = now - self._last_timestamp
            return
        
        self.deltatime = 0.0001
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

        angular_speed = math.pi / 64 # radians per second
        angle_sign = 1.0 if player.turn_state == 'right' else -1.0

        player.facing_angle += angular_speed * angle_sign * self.deltatime


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
        return f"?angle:{player_idx}:{angle}\\"


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

            for player in self.players:
                self.move_player(player)
                self.turn_player(player)

                self.handle_player_client_response(player)


    def handle_player_client_response(self, player: SecretGamePlayer):
        try:
            conn_to_handle = player.conn
            data = conn_to_handle.recv(BUF_SIZE).decode()[:-1] # ignore the ending `\`

            if data.startswith("!car-turn"):
                fields = data.split(':')
                new_turn_state = fields[1]

                player.turn_state = assert_str_is_turn_state(new_turn_state)

            else:
                print(f"ERROR: Invalid client response '{data}'")

        except socket.timeout: pass

