from global_state import GlobalClientState, StrategoGlobalState, WordGolfGlobalState, ValidState
from typing import Callable
from stratego.stratego_types import StrategoBoard, StrategoMoveResult, assert_str_is_color

class ServerCommandParser:
    def __init__(
        self, 
        client_state: GlobalClientState,
        change_game_state: Callable[[ValidState], None],
    ):
        self.client_state = client_state
        self.change_game_state = change_game_state


    def parse_server_command(self, data: str):
        if data.startswith("?game-start"):
            fields = data.split(':')
            game = fields[1]

            if game == 'stratego':
                own_color = fields[2]
                opponent_username = fields[3]

                self.client_state.stratego_state = StrategoGlobalState(
                    own_color=assert_str_is_color(own_color),
                    own_username=self.client_state.username,
                    opponent_username=opponent_username,
                )
                self.change_game_state('in_stratego_game')

            elif game == 'word_golf':
                opponent_username = fields[2]

                self.client_state.word_golf_state = WordGolfGlobalState(
                    own_username=self.client_state.username,
                    opponent_username=opponent_username,
                )
                self.change_game_state('in_word_golf_game')

            else:
                print(f"ERROR: unknown game: '{game}'")


        elif data.startswith("?turn-info"):
            fields = data.split(':')
            current_turn = fields[1]
            board_repr = ':'.join(fields[2:])

            assert self.client_state.stratego_state, "Stratego state was None"

            # Update the turn.
            self.client_state.stratego_state.turn = assert_str_is_color(current_turn)

            # Reset the move result (it no longer needs to be shown, since the board is going 
            # to be reset anyways due to the new turn).
            self.client_state.stratego_state.current_move_result = None

            # Update the board with the data from the server.
            board: StrategoBoard = self.client_state.stratego_state.board
            board.update_elements_with_socket_repr(board_repr)


        elif data.startswith("?move-result"):
            print(f"Received the following move result CMD: {data}")

            fields = data.split(':')
            kind = fields[1]
            r_atk = int(fields[2])
            c_atk = int(fields[3])
            r_def = int(fields[4])
            c_def = int(fields[5])
            move_result = StrategoMoveResult(kind=kind, attacking_pos=(r_atk, c_atk), defending_pos=(r_def, c_def)) # type: ignore

            print(f"Received the following move result: {move_result}")

            assert self.client_state.stratego_state, "Stratego state was None"

            self.client_state.stratego_state.current_move_result = move_result


        elif data.startswith("?update"):
            fields = data.split(':')
            own_points = int(fields[1])
            own_queued_word_amt = int(fields[2])
            opp_points = int(fields[3])
            opp_queued_word_amt = int(fields[4])

            assert self.client_state.word_golf_state, "Word Golf state was None"

            # Sync the (client) global state with the server's state.
            self.client_state.word_golf_state.own_points = own_points
            self.client_state.word_golf_state.opp_points = opp_points
            self.client_state.word_golf_state.own_queued_word_amt = own_queued_word_amt
            self.client_state.word_golf_state.opp_queued_word_amt = opp_queued_word_amt


        elif data.startswith("?feedback-history"):
            fields = data.split(':')
            feedback_hist = fields[1:]
            
            # Quirk with string split means that an empty feedback history is parsed as [''].
            # This `if` statement corrects this.
            if len(feedback_hist) == 1 and feedback_hist[0] == '':
                feedback_hist = []

            assert self.client_state.word_golf_state, "Word Golf state was None"

            self.client_state.word_golf_state.feedback_history = feedback_hist

            # Clear the client-side typed letters once the player gets feedback from the server.
            self.client_state.word_golf_state.typed_letters = []

        elif data.startswith("?stashed-words"):
            fields = data.split(':')
            stashed_words = fields[1:]
            
            # Quirk with string split means that an empty word stash is parsed as [''].
            # This `if` statement corrects this.
            if len(stashed_words) == 1 and stashed_words[0] == '':
                stashed_words = []

            assert self.client_state.word_golf_state, "Word Golf state was None"

            self.client_state.word_golf_state.stashed_words = stashed_words

            print(f"LOG: The stashed words are: {self.client_state.word_golf_state.stashed_words}")

        elif data.startswith("?game-over"):
            fields = data.split(':')
            game = fields[1]
            reason = fields[2]

            if reason == "winner-determined":
                if game == "stratego":
                    winning_color = fields[3]
                    game_over_message = f"The ({winning_color}) player has won!"

                elif game == "word_golf":
                    winner_username = fields[3]
                    game_over_message = f"Player '{winner_username}' has won!"

                else:
                    print(f"ERROR: could not set game-over message; unknown game '{game}'")
                    game_over_message = "ERROR: empty game over message"

            elif reason == "abrupt-end":
                game_over_message = "The game was abruptly ended."

            else:
                print(f"ERROR: The game unexpectedly ended after server sent `{data}`.")
                game_over_message = "MISSING GAME OVER MESSAGE"

            self.client_state.game_over_message = game_over_message
            self.change_game_state('finished_game')

        else:
            print(f"ERROR: Unknown server command: '{data}'")