import socket
from pathlib import Path
import random
import time

from server_types import BUF_SIZE

from .word_golf_types import WordGolfPlayer, WordGolfOccurrence, WordGolfGameResult

class WordGolfGame:
    # The maximum number of tries that a player has for guessing a word.
    MAX_FEEDBACK_HIST_LEN = 6

    def __init__(self, players: list[WordGolfPlayer]):
        if len(players) != 2:
            raise Exception(f"Expected 2 Word Golf players, not {len(players)}")
        
        self.players = players
        
        self.is_running = True

        self.already_solved_words: set[str] = set()

        chosen_words = self.choose_words_for_game()
        for i in range(len(self.players)):
            self.players[i].queued_words = chosen_words[5:] if i == 0 else chosen_words[:5]

        self.result: WordGolfGameResult | None = None
        

    def choose_words_for_game(self) -> list[str]:
        WORD_DB_PATH = Path(__file__).parent / "word.db.txt"
        
        with open(WORD_DB_PATH, "r") as f:
            words = f.read().split('\n')

        # Randomly choose 10 words.
        chosen_words = random.sample(words, 10)
        return chosen_words
    

    def gen_feedback(self, actual_word: str, guess: str) -> str:
        feedback = []

        # These dictionaries are for implementing the 
        # heuristics for marking an out of place letter as 
        # wrong. 
        # i.e. if the actual word is "HONEY" and the guess is "LINEN", then 
        # the second 'N' has a feedback of X even though its in the word.
        actual_letter_freq = {}
        correct_guess_amt = {}

        for i in range(len(actual_word)):
            actual_letter_freq.setdefault(actual_word[i], 0)
            # This is to make sure that `correct_guess_amt` has entries for 
            # all the letters in the actual word.
            correct_guess_amt.setdefault(actual_word[i], 0)
            actual_letter_freq[actual_word[i]] += 1
            
            if guess[i] == actual_word[i]:
                correct_guess_amt[guess[i]] += 1

        for i in range(len(actual_word)):
            # Correct letter guess.
            if actual_word[i] == guess[i]:
                feedback.append(f'O{guess[i]}')
            
            # Letter from guess is in the actual word, but in a different position.
            # AND that there are still remaining "unguessed" occurrences of the letter 
            # left. 
            # NOTE: We need to query with `guess[i]` instead of `actual_word[i]`.
            elif guess[i] in actual_word and correct_guess_amt[guess[i]] < actual_letter_freq[guess[i]]:
                feedback.append(f'!{guess[i]}')

            # Letter from guess is not in the actual word.
            else:
                feedback.append(f'X{guess[i]}')

        return "".join(feedback)
    

    def gen_feedback_history_cmd_for_player(self, player: WordGolfPlayer) -> str:
        return f"?feedback-history:{':'.join(player.feedback_history)}"


    def send_feedback_history_to_player(self, player: WordGolfPlayer):
        # Send the feedback history only to the current player.
        feedback_hist_cmd = self.gen_feedback_history_cmd_for_player(player)
        player.conn.sendall(feedback_hist_cmd.encode())


    def gen_stashed_words_cmd_for_player(self, player: WordGolfPlayer) -> str:
        return f"?stashed-words:{':'.join(player.stashed_words)}"
    

    def send_stashed_words_to_player(self, player: WordGolfPlayer):
        # Send the feedback history only to the current player.
        feedback_hist_cmd = self.gen_stashed_words_cmd_for_player(player)
        player.conn.sendall(feedback_hist_cmd.encode())


    def get_player_opponent_idx(self, player_idx: int) -> int:
        """
        Returns the index of the opposing player i.e. returns 1 if given 0 and 0 if given 1.
        """
        return (player_idx + 1) % 2

    
    def run(self):
        """
        Runs the given game.
        """
        try:
            self.run_main_game_loop()

        # End the game if a connection error occurs.
        except ConnectionResetError:
            self.result = WordGolfGameResult(winner_username=None, abrupt_end=True)
            pass

        # Game ended.
        print("LOG: Word Golf game ended")

        for player in self.players:
            # The result of the game must have been determined already.
            assert self.result

            try:
                # There is a winner.
                if self.result.winner_username is not None:
                    player.conn.sendall(f"?game-over:word_golf:winner-determined:{self.result.winner_username}".encode())

                # The game abruptly ended before finishing normally.
                elif self.result.abrupt_end:
                    player.conn.sendall("?game-over:word_golf:abrupt-end".encode())

                # Since the winner is None, but there wasn't an abrupt end, that means that 
                # there was a tie.
                else:
                    player.conn.sendall("?game-over:word_golf:tie".encode())

            # Do not bother trying to send a game over message if the client's socket is disconnected.
            except ConnectionResetError: pass


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

                # Wait a small delay and then send the player's feedback history.
                time.sleep(0.5)
                self.send_feedback_history_to_player(self.players[curr_idx])

                # Wait a small delay and then send the player's stashed words.
                time.sleep(0.5)
                self.send_stashed_words_to_player(self.players[curr_idx])

            # Receive data from both players until the game determines that client-state needs 
            # to be updated (by setting `update_needed = True`).
            update_needed = False
            while not update_needed:
                for curr_idx in range(len(self.players)):
                    # The index of the player that is not the "current" player.
                    other_idx = self.get_player_opponent_idx(curr_idx)

                    # Based on what this returns, decide whether to update the client's state.
                    occurrence = self.handle_player_client_response(curr_idx)

                    if occurrence is not None:
                        self.manage_occurrence_after_player_action(occurrence)
                        update_needed = True

                # Stop trying to read player data if the game stopped running.
                if not self.is_running:
                    # TODO: after this, the players don't receive updates.
                    # ^^^ this is likely to cause problems so it's a good idea to send 
                    # out one last update before ending the game
                    break


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

                if actual_word == guess:
                    occurence = WordGolfOccurrence(kind='correct_guess', player_idx=curr_player_idx)
                else:
                    occurence = WordGolfOccurrence(kind='wrong_guess', player_idx=curr_player_idx)

                # Save the feedback on the player's feedback history.
                self.players[curr_player_idx].feedback_history.append(feedback)

                if len(self.players[curr_player_idx].feedback_history) == WordGolfGame.MAX_FEEDBACK_HIST_LEN:
                    if occurence.kind != 'correct_guess':
                        occurence = WordGolfOccurrence(kind='ran_out_of_guesses', player_idx=curr_player_idx)

                return occurence
            
            elif data.startswith("!send-stashed-word"):
                fields = data.split(':')
                stashed_word_to_send = fields[1]

                # Player is trying to send a word that they do not have stashed.
                if stashed_word_to_send not in self.players[curr_player_idx].stashed_words:
                    print(f"LOG: Player #{curr_player_idx} is trying to send word '{stashed_word_to_send}' that they do not have stashed.")
                    return None
                
                # Remove the word from the stash.
                self.players[curr_player_idx].stashed_words.remove(stashed_word_to_send)

                occurence = WordGolfOccurrence(
                    kind='sending_stashed_word',
                    player_idx=curr_player_idx,
                    stashed_word=stashed_word_to_send,
                )
                return occurence

            else:
                print(f"ERROR: Invalid client response '{data}'")
                return None # unknown command from client

        except socket.timeout: 
            return None
        

    def manage_occurrence_after_player_action(self, occurrence: WordGolfOccurrence):
        if occurrence.kind == 'wrong_guess':
            print(f"LOG: Player #{occurrence.player_idx} guesses the wrong word (+1 point)")
            self.players[occurrence.player_idx].points += 1

        elif occurrence.kind == 'correct_guess':
            print(f"LOG: Player #{occurrence.player_idx} correctly guessed their word (-5 points)")

            # Remove points from the player. Clamps to 0 if the result is negative.
            curr_pts = self.players[occurrence.player_idx].points
            self.players[occurrence.player_idx].points = max(curr_pts - 5, 0)

            self.switch_player_current_word(occurrence)

        elif occurrence.kind == 'ran_out_of_guesses':
            print(f"LOG: Player #{occurrence.player_idx} ran out of guesses (+3 points)")
            self.players[occurrence.player_idx].points += 3

            self.switch_player_current_word(occurrence)

        elif occurrence.kind == 'sending_stashed_word':
            assert occurrence.stashed_word, "Logic error, stashed word should not have been None."

            print(f"LOG: Player #{occurrence.player_idx} sent stashed word '{occurrence.stashed_word}'")
            
            # Change the opponent's current word.
            opponent_idx = self.get_player_opponent_idx(occurrence.player_idx)
            self.players[opponent_idx].queued_words.append(occurrence.stashed_word)

        else:
            print(f"ERROR: unhandled occurence kind '{occurrence.kind}'")


    def reset_player_word_associated_data(self, player_idx: int):
        curr_player = self.players[player_idx]

        # Reset the 'already guessed words' set and the feedback history.
        curr_player.already_guessed_words = set()
        curr_player.feedback_history = []


    def switch_player_current_word(self, occurrence: WordGolfOccurrence):
        player_idx = occurrence.player_idx

        self.reset_player_word_associated_data(player_idx)

        if len(self.players[player_idx].queued_words) > 1:
            guessed_word = self.players[player_idx].queued_words.pop()
            print(f"LOG: Player '{self.players[player_idx].username}' is no longer guessing '{guessed_word}' now their word is '{self.players[player_idx].queued_words[-1]}'")
            
            if guessed_word not in self.already_solved_words:
                self.already_solved_words.add(guessed_word)

                # If a guessed word has not already been guessed before, 
                # and the player has correctly guessed the word, then it is 
                # added to their stash.
                if occurrence.kind == 'correct_guess':
                    self.players[player_idx].stashed_words.add(guessed_word)

        # The current player has run out of queued words.
        else:
            self.on_player_ran_out_of_words(player_idx)


    def on_player_ran_out_of_words(self, player_idx: int):
        FIRST_FINISH_BONUS = 5

        curr_pts = self.players[player_idx].points
        curr_pts = max(0, curr_pts - FIRST_FINISH_BONUS)
        self.players[player_idx].points = curr_pts

        other_idx = self.get_player_opponent_idx(player_idx)

        # The player with the least amount of points wins. 
        # Otherwise there is a tie.
        if self.players[player_idx].points < self.players[other_idx].points:
            self.declare_winner(player_idx)

        elif self.players[player_idx].points > self.players[other_idx].points:
            self.declare_winner(other_idx)

        else:
            self.declare_tie()


    def declare_winner(self, player_idx: int):
        """
        Ends the game and declares a winner.
        """
        winner_username = self.players[player_idx].username
        print(f"LOG: Player '{winner_username}' has won.")

        self.is_running = False
        self.result = WordGolfGameResult(winner_username, abrupt_end=False)


    def declare_tie(self):
        self.is_running = False
        self.result = WordGolfGameResult(winner_username=None, abrupt_end=False)
