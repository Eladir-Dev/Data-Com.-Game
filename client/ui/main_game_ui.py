import pygame
import queue
import threading
from games.stratego.deck_selection import StrategoSettingsWindow
from common_types.global_state import GlobalClientState, ValidState
import networking.socket_client as socket_client
from common_types.game_types import SCREEN_WIDTH, SCREEN_HEIGHT
import games.stratego.stratego_game as stratego_game
import games.word_golf.word_golf_game as word_golf_game
from ui.main_game_ui_sub_menus import MainGameSubMenus
from networking.server_cmd_interpreter import ServerCommandInterpreter

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

        self.server_cmd_interpreter = ServerCommandInterpreter(
            client_state=self.client_state,
            change_game_state=self.change_game_state,
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
                self.server_cmd_interpreter.interpret_server_command(data)

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
                game_over_msg = self.client_state.game_over_message
                assert game_over_msg, "Game Over Message was None"
                self.sub_menus.set_game_over_message(game_over_msg)

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


