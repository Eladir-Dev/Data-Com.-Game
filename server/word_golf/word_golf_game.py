import socket
from pathlib import Path
import random

from server_types import BUF_SIZE

from .word_golf_types import WordGolfPlayer, WordGolfOccurrence

class WordGolfGame:
    # The feedback that a correct guess would generate.
    CORRECT_FEEDBACK = "OOOOO"

    # The maximum number of tries that a player has for guessing a word.
    MAX_FEEDBACK_HIST_LEN = 6

    def __init__(self, players: list[WordGolfPlayer]):
        if len(players) != 2:
            raise Exception(f"Expected 2 Word Golf players, not {len(players)}")
        
        self.players = players
        
        self.is_running = True

        chosen_words = self.choose_words_for_game()
        for i in range(len(self.players)):
            self.players[i].queued_words = chosen_words[5:] if i == 0 else chosen_words[:5]
        

    def choose_words_for_game(self) -> list[str]:
        WORD_DB_PATH = Path(__file__).parent / "word.db.txt"
        
        with open(WORD_DB_PATH, "r") as f:
            words = f.read().split('\n')

        # Randomly choose 10 words.
        chosen_words = random.sample(words, 10)
        return chosen_words
    

    def gen_feedback(self, actual_word: str, guess: str) -> str:
        feedback = []

        for i in range(len(actual_word)):
            # Correct letter guess.
            if actual_word[i] == guess[i]:
                feedback.append('O')
            
            # Letter from guess is in the actual word, but in a different position.
            elif guess[i] in actual_word:
                feedback.append('!')

            # Letter from guess is not in the actual word.
            else:
                feedback.append('X')

        return "".join(feedback)
    

    def gen_feedback_history_cmd_for_player(self, player: WordGolfPlayer) -> str:
        return f"?feedback-history:{':'.join(player.feedback_history)}"

    
    def run(self):
        """
        Runs the given game.
        """
        try:
            self.run_main_game_loop()

        # End the game if a connection error occurs.
        except ConnectionResetError:
            # self.result = StrategoGameResult(None, abrupt_end=True)
            pass

        # Game ended.
        print("LOG: Word Golf game ended")


    def run_main_game_loop(self):
        """
        Runs the main part of the game loop.
        """
        while self.is_running:
            # Send updates to each player to sync state.
            for curr_idx in range(len(self.players)):
                # The index of the player that is not the "current" player.
                other_idx = (curr_idx + 1) % 2

                curr_points = self.players[curr_idx].points
                curr_queued_word_amt = len(self.players[curr_idx].queued_words)

                other_points = self.players[other_idx].points
                other_queued_word_amt = len(self.players[other_idx].queued_words)

                data = f"?update:{curr_points}:{curr_queued_word_amt}:{other_points}:{other_queued_word_amt}"

                self.players[curr_idx].conn.sendall(data.encode())

            # Receive data from both players until the game determines that client-state needs 
            # to be updated (by setting `update_needed = True`).
            update_needed = False
            while not update_needed:
                for curr_idx in range(len(self.players)):
                    # The index of the player that is not the "current" player.
                    other_idx = (curr_idx + 1) % 2

                    # NOTE: Since the occurrence provides a player index, these cases can be 
                    # moved to another method.

                    # Based on what this returns, decide whether to update the client's state.
                    occurence = self.handle_player_client_response(curr_idx)

                    if occurence is not None:
                        if occurence.kind == 'wrong_guess':
                            print(f"LOG: Player #{occurence.player_idx} guesses the wrong word (+1 point)")
                            self.players[occurence.player_idx].points += 1

                        # TODO: for the bottom 2 cases, swap out / remove the current queued word; no point in keeping the same one.
                        # ALSO: reset things like the `.already_guessed_words` set and the feedback history.

                        elif occurence.kind == 'correct_guess':
                            print(f"LOG: Player #{occurence.player_idx} correctly guessed their word (-5 points)")

                            # Remove points from the player. Clamps to 0 if the result is negative.
                            curr_pts = self.players[occurence.player_idx].points
                            self.players[occurence.player_idx].points = max(curr_pts - 5, 0)

                        elif occurence.kind == 'ran_out_of_guesses':
                            print(f"LOG: Player #{occurence.player_idx} ran out of guesses (+3 points)")
                            self.players[occurence.player_idx].points += 3

                        else:
                            print(f"ERROR: unhandled occurence kind '{occurence.kind}'")

                        update_needed = True


    def handle_player_client_response(self, curr_player_idx: int) -> WordGolfOccurrence | None:
        try:
            conn_to_handle = self.players[curr_player_idx].conn
            data = conn_to_handle.recv(BUF_SIZE).decode()

            if data.startswith("!guess"):
                fields = data.split(':')
                guess = fields[1].upper()

                if guess in self.players[curr_player_idx].already_guessed_words:
                    print(f"LOG: Player #{curr_player_idx} has already tried guessing: '{guess}'")
                    return None
                
                # Mark the guessed word as already guessed (for avoiding re-sending the same word).
                self.players[curr_player_idx].already_guessed_words.add(guess)

                # Get the actual word that the player needs to guess.
                actual_word = self.players[curr_player_idx].queued_words[-1]

                print(f"LOG: received guess '{guess}'; actual word was '{actual_word}'")

                occurence: WordGolfOccurrence | None = None

                feedback = self.gen_feedback(actual_word, guess)

                if feedback != WordGolfGame.CORRECT_FEEDBACK:
                    occurence = WordGolfOccurrence(kind='wrong_guess', player_idx=curr_player_idx)
                else:
                    occurence = WordGolfOccurrence(kind='correct_guess', player_idx=curr_player_idx)

                # Save the feedback on the player's feedback history.
                self.players[curr_player_idx].feedback_history.append(feedback)

                # Send the feedback history only to the current player.
                feedback_hist_cmd = self.gen_feedback_history_cmd_for_player(self.players[curr_player_idx])
                conn_to_handle.sendall(feedback_hist_cmd.encode())

                if len(self.players[curr_player_idx].feedback_history) == WordGolfGame.MAX_FEEDBACK_HIST_LEN:
                    if occurence.kind != 'correct_guess':
                        occurence = WordGolfOccurrence(kind='ran_out_of_guesses', player_idx=curr_player_idx)

                return occurence

            else:
                print(f"ERROR: Invalid client response '{data}'")
                return None # unknown command from client

        except socket.timeout: 
            return None

