from common_types.global_state import GlobalClientState, StrategoGlobalState, WordGolfGlobalState, ValidState
from typing import Callable
from games.stratego.stratego_types import StrategoBoard, StrategoColor, StrategoMoveResult, assert_str_is_color, ROWS, COLS

import networking.validator as validator

class ServerCommandInterpreter:
    """
    This class parses and interprets server commands. Modifies the given :py:attr:`client_state` object 
    and/or calls the given :py:attr:`change_game_state` callback depending on the received command. Raises 
    :py:class:`ValueError` when an invalid command is encountered.
    """
    def __init__(
        self, 
        client_state: GlobalClientState,
        change_game_state: Callable[[ValidState], None],
    ):
        self.client_state = client_state
        self.change_game_state = change_game_state


    def interpret_server_command(self, data: str):
        if data.startswith("?game-start"):
            fields = validator.assert_field_min_amount_valid(data.split(':'), 3)
            game = fields[1]

            if game == 'stratego':
                own_color = assert_str_is_color(fields[2])
                opponent_username = validator.assert_valid_username(fields[3])

                self.game_start_stratego(own_color, opponent_username)

            elif game == 'word_golf':
                opponent_username = validator.assert_valid_username(fields[2])

                self.game_start_word_golf(opponent_username)

            else:
                print(f"ERROR: unknown game: '{game}'")


        elif data.startswith("?turn-info"):
            fields = validator.assert_field_amount_valid(data.split(':'), 2 + ROWS * COLS)
            current_turn = assert_str_is_color(fields[1])
            board_repr = ':'.join(fields[2:])

            self.update_using_stratego_turn_info(current_turn, board_repr)


        elif data.startswith("?move-result"):
            print(f"Received the following move result CMD: {data}")

            fields = validator.assert_field_amount_valid(data.split(':'), 6)
            kind = fields[1]
            r_atk = int(fields[2])
            c_atk = int(fields[3])
            r_def = int(fields[4])
            c_def = int(fields[5])
            move_result = StrategoMoveResult(kind=kind, attacking_pos=(r_atk, c_atk), defending_pos=(r_def, c_def)) # type: ignore

            self.receive_stratego_move_result(move_result)


        elif data.startswith("?update"):
            fields = validator.assert_field_amount_valid(data.split(':'), 5)
            own_points = int(fields[1])
            own_queued_word_amt = int(fields[2])
            opp_points = int(fields[3])
            opp_queued_word_amt = int(fields[4])

            self.receive_word_golf_general_update(
                own_points,
                own_queued_word_amt,
                opp_points,
                opp_queued_word_amt,
            )


        elif data.startswith("?feedback-history"):
            fields = validator.assert_field_min_amount_valid(data.split(':'), 2)
            feedback_hist = fields[1:]
            
            # Quirk with string split means that an empty feedback history is parsed as [''].
            # This `if` statement corrects this.
            if len(feedback_hist) == 1 and feedback_hist[0] == '':
                feedback_hist = []

            self.receive_word_golf_feedback_history(feedback_hist)


        elif data.startswith("?stashed-words"):
            fields = validator.assert_field_min_amount_valid(data.split(':'), 2)
            stashed_words = fields[1:]
            
            # Quirk with string split means that an empty word stash is parsed as [''].
            # This `if` statement corrects this.
            if len(stashed_words) == 1 and stashed_words[0] == '':
                stashed_words = []

            self.update_own_word_golf_stashed_words(stashed_words)


        elif data.startswith("?alert"):
            fields = validator.assert_field_min_amount_valid(data.split(':'), 2)
            alert_fields = fields[1:]

            # NOTE: This operation should be a separate method, it is duplicated in a lot of cases.
            if len(alert_fields) == 1 and alert_fields[0] == '':
                alert_fields = []

            alert_fields = validator.assert_field_min_amount_valid(alert_fields, 1)

            self.receive_latest_word_golf_alert(alert_fields)


        elif data.startswith("?game-over"):
            fields = validator.assert_field_min_amount_valid(data.split(':'), 3)
            game = fields[1]
            reason = fields[2]

            game_over_message = self.get_game_over_message(reason, game, all_received_fields=fields)

            self.client_state.game_over_message = game_over_message
            self.change_game_state('finished_game')

        else:
            print(f"ERROR: Unknown server command: '{data}'")


    def game_start_stratego(self, own_color: StrategoColor, opponent_username: str):
        self.client_state.stratego_state = StrategoGlobalState(
            own_color=own_color,
            own_username=self.client_state.username,
            opponent_username=opponent_username,
        )
        self.change_game_state('in_stratego_game')


    def game_start_word_golf(self, opponent_username: str):
        self.client_state.word_golf_state = WordGolfGlobalState(
            own_username=self.client_state.username,
            opponent_username=opponent_username,
        )
        self.change_game_state('in_word_golf_game')


    def update_using_stratego_turn_info(self, current_turn: StrategoColor, board_repr: str):
        assert self.client_state.stratego_state, "Stratego state was None"

        # Update the turn.
        self.client_state.stratego_state.turn = current_turn

        # Reset the move result (it no longer needs to be shown, since the board is going 
        # to be reset anyways due to the new turn).
        self.client_state.stratego_state.current_move_result = None

        # Update the board with the data from the server.
        board: StrategoBoard = self.client_state.stratego_state.board
        board.update_elements_with_socket_repr(board_repr)


    def receive_stratego_move_result(self, move_result: StrategoMoveResult):
        assert self.client_state.stratego_state, "Stratego state was None"

        self.client_state.stratego_state.current_move_result = move_result


    def receive_word_golf_general_update(
        self,
        own_points: int,
        own_queued_word_amt: int,
        opp_points: int,
        opp_queued_word_amt: int,
    ):
        assert self.client_state.word_golf_state, "Word Golf state was None"

        # Sync the (client) global state with the server's state.
        self.client_state.word_golf_state.own_points = own_points
        self.client_state.word_golf_state.opp_points = opp_points
        self.client_state.word_golf_state.own_queued_word_amt = own_queued_word_amt
        self.client_state.word_golf_state.opp_queued_word_amt = opp_queued_word_amt

        # Clear the alerts.
        # NOTE: This so that alerts that are no longer relevant don't clutter the UI, 
        # but if a better UI solution is found, the alerts wouldn't need to be cleared every general update.
        self.client_state.word_golf_state.received_alerts = []


    def receive_word_golf_feedback_history(self, feedback_hist: list[str]):
        assert self.client_state.word_golf_state, "Word Golf state was None"

        self.client_state.word_golf_state.feedback_history = feedback_hist

        # Clear the client-side typed letters once the player gets feedback from the server.
        self.client_state.word_golf_state.typed_letters = []


    def update_own_word_golf_stashed_words(self, stashed_words: list[str]):
        assert self.client_state.word_golf_state, "Word Golf state was None"

        self.client_state.word_golf_state.stashed_words = stashed_words

        print(f"LOG: The stashed words are: {self.client_state.word_golf_state.stashed_words}")


    def receive_latest_word_golf_alert(self, alert_fields: list[str]):
        assert self.client_state.word_golf_state, "Word Golf state was None"

        kind = alert_fields[0]

        if kind == "received-word":
            opp_username = self.client_state.word_golf_state.opp_username
            own_word_amt = self.client_state.word_golf_state.own_queued_word_amt

            self.client_state.word_golf_state.received_alerts\
                .append(f"'{opp_username}' sent a word! Now you have {own_word_amt} words to solve.")

        else:
            print(f"ERROR: unknown alert kind '{kind}'")


    def get_game_over_message(self, reason: str, game: str, all_received_fields: list[str]):
        if reason == "winner-determined":
            if game == "stratego":
                winning_color = all_received_fields[3]
                return f"The ({winning_color}) player has won!"

            elif game == "word_golf":
                winner_username = all_received_fields[3]
                return f"Player '{winner_username}' has won!"

            else:
                print(f"ERROR: could not set game-over message; unknown game '{game}'")
                return "ERROR: empty game over message"

        elif reason == "abrupt-end":
            return "The game was abruptly ended."
        
        elif reason == "tie":
            return "No winner could be determined as there was a tie."

        else:
            print(f"ERROR: The game unexpectedly ended after server sent `{''.join(all_received_fields)}`.")
            return "MISSING GAME OVER MESSAGE"
