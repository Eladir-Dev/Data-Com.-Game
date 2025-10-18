import pygame
import queue
import threading
from stratego.deck_selection import StrategoSettingsWindow
from global_state import GlobalClientState, StrategoGlobalState, ValidState, WordGolfGlobalState
import socket_client
from game_types import SCREEN_WIDTH, SCREEN_HEIGHT
from stratego.stratego_types import StrategoBoard, StrategoMoveResult, assert_str_is_color
import stratego.stratego_game as stratego_game
import word_golf.word_golf_game as word_golf_game
from main_game_ui_sub_menus import MainGameSubMenus

class MainGameUI:
    def __init__(self):
        self.client_state = GlobalClientState(
            username="johndoe", 
            server_ip="127.0.0.1", # localhost by default
            game_state='main_menu',
        )

        self.server_cmd_queue: queue.Queue[str] = queue.Queue()
        self.client_cmd_queue: queue.Queue[str] = queue.Queue()

        SOCKET_CLIENT_THREAD = threading.Thread(target=socket_client.connect, args=(self.server_cmd_queue, self.client_cmd_queue))
        SOCKET_CLIENT_THREAD.daemon = True # Allows the program to exit even if the thread is running.
        SOCKET_CLIENT_THREAD.start()

        pygame.init()
        self.surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.deck_selection_menu = StrategoSettingsWindow(
            self.surface, 
            go_to_prev_menu=lambda: self.change_game_state('main_menu'), 
            go_to_start=self.start_loading_stratego_game,
            player_data=self.client_state,
        )

        self.sub_menus = MainGameSubMenus(
            client_state=self.client_state,
            change_game_state=self.change_game_state,
            start_loading_stratego_game=self.start_loading_stratego_game,
            start_loading_word_wolf_game=self.start_loading_word_wolf_game,
        )


    def change_game_state(self, new_state: ValidState):
        """
        Changes the game's state. Used to determine the screen that is being shown.
        """
        self.client_state.game_state = new_state
    

    def start(self):
        while True:
            while not self.server_cmd_queue.empty():
                data = self.server_cmd_queue.get()

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
                    self.client_state.stratego_state.turn = current_turn # type: ignore

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

                    
                    label = self.sub_menus.game_over_menu.get_widget('game_over_label')
                    assert label
                    label.set_title(game_over_message)

                    self.change_game_state('finished_game')

                else:
                    print(f"ERROR: Unknown server command: '{data}'")

            events = pygame.event.get()
            for event in events:
                if event.type == self.sub_menus.update_loading:
                    progress = self.sub_menus.loading.get_widget("1")
                    assert progress # fixes null errors; crashes if progress is somehow `None`

                    progress.set_value(progress.get_value() + 1)
                    if progress.get_value() == 100:
                        pygame.time.set_timer(self.sub_menus.update_loading, 0)
                if event.type == pygame.QUIT:
                    exit()

            game_state: ValidState = self.client_state.game_state

            if game_state == 'main_menu':
                self.sub_menus.title_screen.update(events)
                self.sub_menus.title_screen.draw(self.surface)
                if (self.sub_menus.title_screen.get_current().get_selected_widget()):
                    self.sub_menus.arrow.draw(self.surface, self.sub_menus.title_screen.get_current().get_selected_widget())

            elif game_state == 'in_deck_selection_state':
                self.deck_selection_menu.update(events)

            elif game_state == 'in_stratego_game':
                assert self.client_state.stratego_state, "Stratego state was None"

                # Display Stratego game window.
                move_cmd = stratego_game.stratego_update(events, self.surface, self.client_state.stratego_state)

                if move_cmd is not None:
                    self.client_cmd_queue.put(move_cmd)

            elif game_state == 'loading_stratego_game':
                self.sub_menus.loading_window_stratego.update(events)
                self.sub_menus.loading_window_stratego.draw(self.surface)

            elif game_state == 'finished_game':
                self.sub_menus.game_over_menu.update(events)
                self.sub_menus.game_over_menu.draw(self.surface)

            elif game_state == 'in_word_golf_game':
                assert self.client_state.word_golf_state, "Word Golf state was None"

                update_result = word_golf_game.word_golf_update(events, self.surface, self.client_state.word_golf_state)

                if update_result.guess_cmd is not None:
                    self.client_cmd_queue.put(update_result.guess_cmd)

                # NOTE: This uses `elif` instead of another `if` to avoid possibly sending them at the same time.
                # Sending both at the same time might overload the server.
                # The chances that both a guess CMD and a stashed word CMD are sent at the same frame are low anyways.
                elif update_result.stashed_word_cmd is not None:
                    self.client_cmd_queue.put(update_result.stashed_word_cmd)

            elif game_state == 'loading_word_golf_game':
                self.sub_menus.loading_window_word_golf.update(events)
                self.sub_menus.loading_window_word_golf.draw(self.surface)

            else:
                print(f"ERROR: unhandled game state '{game_state}'")

            pygame.display.update()


    def start_loading_stratego_game(self):
        deck = self.client_state.stratego_starting_deck_repr
        assert deck, "Stratego starting deck has not been set"

        self.change_game_state('loading_stratego_game')

        # Send the user's username and starting deck to the socket client (which then forwards it to the server).
        self.client_cmd_queue.put(
            f"!want-play-game:stratego:{self.client_state.username}:{self.client_state.server_ip}:{deck}"
        )


    def start_loading_word_wolf_game(self):
        self.change_game_state('loading_word_golf_game')

        # Send the user's username to the socket client (which then forwards it to the server).
        self.client_cmd_queue.put(
            f"!want-play-game:word_golf:{self.client_state.username}:{self.client_state.server_ip}"
        )


