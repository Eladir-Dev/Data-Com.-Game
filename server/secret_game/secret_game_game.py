from secret_game.secret_game_types import SecretGamePlayer
from server_types import BUF_SIZE
import socket

class SecretGameGame:
    def __init__(self, players: list[SecretGamePlayer]):
        self.players = players

        self.is_running = True


    # TODO: everything
    
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

        # # Game ended.
        # print("LOG: Word Golf game ended")

        # for player in self.players:
        #     # The result of the game must have been determined already.
        #     assert self.result

        #     try:
        #         # There is a winner.
        #         if self.result.winner_username is not None:
        #             player.conn.sendall(f"?game-over:word_golf:winner-determined:{self.result.winner_username}".encode())

        #         # The game abruptly ended before finishing normally.
        #         elif self.result.abrupt_end:
        #             player.conn.sendall("?game-over:word_golf:abrupt-end".encode())

        #         # Since the winner is None, but there wasn't an abrupt end, that means that 
        #         # there was a tie.
        #         else:
        #             player.conn.sendall("?game-over:word_golf:tie".encode())

        #     # Do not bother trying to send a game over message if the client's socket is disconnected.
        #     except ConnectionResetError: pass


    def run_main_game_loop(self):
        """
        Runs the main part of the game loop.
        """
        while self.is_running:
            for player in self.players:
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

