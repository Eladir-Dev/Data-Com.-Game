from secret_game.secret_game_types import SecretGamePlayer, Vector, SecretGameResult
from server_types import BUF_SIZE
import socket
import time
import math

class SecretGameGame:
    def __init__(self, players: list[SecretGamePlayer]):
        self.players = players

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
        player.position += movement


    def build_pos_cmd_for_player(self, player_idx: int) -> str:
        pos = self.players[player_idx].position
        return f"?pos:{player_idx}:{int(pos.x)}:{int(pos.y)}\\"


    def send_position_commands(self):
        move_cmds = [self.build_pos_cmd_for_player(i) for i in range(len(self.players))]

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
            # self.result = WordGolfGameResult(winner_username=None, abrupt_end=True)
            pass

        # Game ended.
        print("LOG: A Secret Game ended")

        for player in self.players:
            # The result of the game must have been determined already.
            assert self.result

            try:
                # There is a winner.
                if self.result.winner_idx is not None:
                    player.conn.sendall(f"?game-over:secret_game:winner-determined:{self.result.winner_idx}".encode())

                # The game abruptly ended before finishing normally.
                elif self.result.abrupt_end:
                    player.conn.sendall("?game-over:secret_game:abrupt-end".encode())

                # Since the winner is None, but there wasn't an abrupt end, that means that 
                # there was a tie.
                else:
                    player.conn.sendall("?game-over:secret_game:tie".encode())

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

            for player in self.players:
                self.move_player(player)
                self.send_position_commands()

                self.handle_player_client_response(player)


    def handle_player_client_response(self, player: SecretGamePlayer):
        try:
            conn_to_handle = player.conn
            data = conn_to_handle.recv(BUF_SIZE).decode()

            if data.startswith("!guess"):
                pass
                # fields = data.split(':')
                # guess = fields[1].upper()

                # if guess in self.players[curr_player_idx].already_guessed_words:
                #     print(f"LOG: Player #{curr_player_idx} has already tried guessing: '{guess}'")
                #     return None
                
                # # Mark the guessed word as already guessed (for avoiding re-sending the same word).
                # self.players[curr_player_idx].already_guessed_words.add(guess)

                # # Get the actual word that the player needs to guess.
                # actual_word = self.players[curr_player_idx].queued_words[-1]

                # print(f"LOG: received guess '{guess}'; actual word was '{actual_word}'")

                # occurence: WordGolfOccurrence | None = None

                # feedback = self.gen_feedback(actual_word, guess)

                # if actual_word == guess:
                #     occurence = WordGolfOccurrence(kind='correct_guess', player_idx=curr_player_idx)
                # else:
                #     occurence = WordGolfOccurrence(kind='wrong_guess', player_idx=curr_player_idx)

                # # Save the feedback on the player's feedback history.
                # self.players[curr_player_idx].feedback_history.append(feedback)

                # if len(self.players[curr_player_idx].feedback_history) == WordGolfGame.MAX_FEEDBACK_HIST_LEN:
                #     if occurence.kind != 'correct_guess':
                #         occurence = WordGolfOccurrence(kind='ran_out_of_guesses', player_idx=curr_player_idx)

                # return occurence
            
            elif data.startswith("!send-stashed-word"):
                pass
                # fields = data.split(':')
                # stashed_word_to_send = fields[1]

                # # Player is trying to send a word that they do not have stashed.
                # if stashed_word_to_send not in self.players[curr_player_idx].stashed_words:
                #     print(f"LOG: Player #{curr_player_idx} is trying to send word '{stashed_word_to_send}' that they do not have stashed.")
                #     return None
                
                # # Remove the word from the stash.
                # self.players[curr_player_idx].stashed_words.remove(stashed_word_to_send)

                # occurence = WordGolfOccurrence(
                #     kind='sending_stashed_word',
                #     player_idx=curr_player_idx,
                #     stashed_word=stashed_word_to_send,
                # )
                # return occurence
                

            else:
                pass
                # print(f"ERROR: Invalid client response '{data}'")
                # return None # unknown command from client

        except socket.timeout: pass

