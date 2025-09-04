import socket
from pathlib import Path
import random

from server_types import BUF_SIZE

from .word_golf_types import WordGolfPlayer

class WordGolfGame:
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

                    # TODO: This handling method should return something.
                    # Based on what this returns, decide whether to update the client's state.
                    self.handle_player_client_response(curr_idx)


    # TODO: What should this method return? It returns `str` in the happy-case as a placeholder 
    # for now, but it should probably return a specialized type, like the handle client method 
    # in Stratego does.
    def handle_player_client_response(self, curr_player_idx: int) -> str | None:
        try:
            conn_to_handle = self.players[curr_player_idx].conn
            data = conn_to_handle.recv(BUF_SIZE).decode()

            if data.startswith("!guess"):
                fields = data.split(':')
                guess = fields[1].upper()

                actual_word = self.players[curr_player_idx].queued_words[-1]

                # TODO: Send this only to the current player.
                feedback = self.gen_feedback(actual_word, guess)

                # TODO: actually process the guess
                print(f"ERROR: handling guesses is not implemented yet; received guess '{guess}'; actual word was '{actual_word}'")
                print(f"Feedback: '{feedback}'")

                return None

            else:
                print(f"ERROR: Invalid client response '{data}'")
                return None # unknown command from client

        except socket.timeout: 
            return None

