import pygame
import queue
import threading
#from games.stratego.st_custom_game import StrategoCustomsWindow
from games.stratego.deck_selection import StrategoSettingsWindow
from common_types.global_state import GlobalClientState, ValidState
import networking.socket_client as socket_client
from common_types.game_types import SCREEN_WIDTH, SCREEN_HEIGHT
import games.stratego.stratego_game as stratego_game
import games.word_golf.word_golf_game as word_golf_game
import games.secret_game.secret_game_game as secret_game_game
import games.lore.lore_update as lore_update
from ui.main_game_ui_sub_menus import MainGameSubMenus
from games.secret_game.secret_game_background_activator import SecretGameBackgroundActivator
from networking.server_cmd_interpreter import ServerCommandInterpreter
from games.secret_dlc_store.secret_dlc_store import start_getting_dlc
from games.secret_dlc_store.secret_dlc_store_update import SecretDLCStoreUpdate
from ui import music_player

class MainGameUI:
    def __init__(self):
        self.client_state = GlobalClientState(
            username="johndoe", 
            server_ip="127.0.0.1", # localhost by default
            game_state='main_menu',
        )

        self.server_cmd_queue: queue.Queue[str] = queue.Queue()
        self.client_cmd_queue: queue.Queue[str] = queue.Queue()

        self.secret_dlc_store_update_queue: queue.Queue[SecretDLCStoreUpdate] = queue.Queue()

        SOCKET_CLIENT_THREAD = threading.Thread(target=socket_client.connect, args=(self.server_cmd_queue, self.client_cmd_queue))
        SOCKET_CLIENT_THREAD.daemon = True # Allows the program to exit even if the thread is running.
        SOCKET_CLIENT_THREAD.start()

        pygame.init()
        pygame.mixer.init()
        self.surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        # ======Stratego menus (before game start)======#

        self.deck_selection_menu = StrategoSettingsWindow(
            self.surface, 
            go_to_prev_menu=lambda: self.change_game_state('main_menu'), 
            go_to_start=self.start_loading_stratego_game,
            player_data=self.client_state,
        )
        # ==============================================#

        self.sub_menus = MainGameSubMenus(
            client_state=self.client_state,
            change_game_state=self.change_game_state,
            start_loading_stratego_game=self.start_loading_stratego_game,
            start_loading_word_wolf_game=self.start_loading_word_wolf_game,
            start_intalling_secret_dlc_game=self.start_intalling_secret_dlc_game,
        )

        self.server_cmd_interpreter = ServerCommandInterpreter(
            client_state=self.client_state,
            change_game_state=self.change_game_state,
        )

        # Very important.
        self.secret_game_background_activator = SecretGameBackgroundActivator(
            client_state=self.client_state,
            start_loading_secret_game=self.start_loading_secret_game,

            # This is unsafe vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
            secret_key_hash="f1e7f77e70f7db539b79e8c827f6bed02aab95a31248ec0926c593bf5b1c71f9",
        )


    def change_game_state(self, new_state: ValidState):
        """
        Changes the game's state. Used to determine the screen that is being shown.
        """
        self.client_state.game_state = new_state

        if new_state == 'in_stratego_game':
            music_player.play_stratego_bg_music()

        elif new_state == 'in_word_golf_game':
            music_player.play_word_golf_bg_music()

        elif new_state == 'in_secret_game':
            music_player.play_secret_game_bg_music()

        elif new_state == 'in_lore':
            music_player.play_lore_bg_music()

        # Stop the music (if any was playing) if a game ended.
        elif new_state == 'finished_game':
            music_player.stop_all_bg_music()
    

    def start(self):
        while True:
            self.receive_server_commands()

            self.receive_secret_dlc_store_updates()

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    # Very important.
                    self.secret_game_background_activator.read_user_key_press(event.unicode)

                if event.type == pygame.QUIT:
                    exit()

            game_state: ValidState = self.client_state.game_state

            self.sub_menus.general_update()

            if game_state == 'main_menu':
                self.sub_menus.title_screen.update(events)
                self.sub_menus.title_screen.draw(self.surface)
                if (self.sub_menus.title_screen.get_current().get_selected_widget()):
                    self.sub_menus.arrow.draw(self.surface, self.sub_menus.title_screen.get_current().get_selected_widget())

            #======Stratego menus (before game start)======#
            elif game_state == 'in_deck_selection_state':
                self.deck_selection_menu.update(events)
            # ==============================================#

            elif game_state == 'in_stratego_game':
                assert self.client_state.stratego_state, "Stratego state was None"

                # Display Stratego game window.
                move_cmd = stratego_game.stratego_update(events, self.surface, self.client_state.stratego_state)

                if move_cmd is not None:
                    self.client_cmd_queue.put(move_cmd)

            elif game_state == 'loading_stratego_game':
                self.sub_menus.loading_window_stratego.update(events)
                self.sub_menus.loading_window_stratego.draw(self.surface)

            elif game_state == 'loading_word_golf_game':
                self.sub_menus.loading_window_word_golf.update(events)
                self.sub_menus.loading_window_word_golf.draw(self.surface)

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

            elif game_state == 'loading_secret_game':
                self.sub_menus.loading_window_secret_game.update(events)
                self.sub_menus.loading_window_secret_game.draw(self.surface)

            elif game_state == 'in_secret_game':
                assert self.client_state.secret_game_state, "Secret Game state was None"

                car_turn_cmd = secret_game_game.secret_game_update(events, self.surface, self.client_state.secret_game_state)

                if car_turn_cmd is not None:
                    self.client_cmd_queue.put(car_turn_cmd)

            elif game_state == 'in_secret_dlc_store':
                self.sub_menus.secret_dlc_store_menu.update(events)
                self.sub_menus.secret_dlc_store_menu.draw(self.surface)

            elif game_state == 'in_secret_dlc_game':
                # Blank screen since the (secret) DLC runs as another executable.
                self.surface.fill((0, 0, 0))

            elif game_state == 'in_lore':
                assert self.client_state.lore_state, "Lore state was None"

                lore_update.lore_update(events, self.surface, self.client_state.lore_state)

            elif game_state == 'finished_game':
                game_over_msg = self.client_state.game_over_message
                assert game_over_msg, "Game Over Message was None"
                self.sub_menus.set_game_over_message(game_over_msg)

                self.sub_menus.game_over_menu.update(events)
                self.sub_menus.game_over_menu.draw(self.surface)

            else:
                print(f"ERROR: unhandled game state '{game_state}'")

            pygame.display.update()


    def receive_server_commands(self):
        while not self.server_cmd_queue.empty():
            data = self.server_cmd_queue.get()
            self.server_cmd_interpreter.interpret_server_command(data)


    def receive_secret_dlc_store_updates(self):
        while not self.secret_dlc_store_update_queue.empty():
            update = self.secret_dlc_store_update_queue.get()

            if update.kind == 'download_progress':
                self.client_state.secret_dlc_download_percentage = update.percentage

            elif update.kind == 'installation_finish':
                self.change_game_state('in_secret_dlc_game')

            elif update.kind == 'game_finish':
                self.client_state.is_already_downloading_dlc = False
                self.change_game_state('main_menu')
            
            elif update.kind == 'error':
                print("ERROR: Could not install DLC.")
                self.client_state.is_already_downloading_dlc = False
                self.change_game_state('main_menu')

            else:
                print(f"Error: unknown secret DLC store update: '{update}'")


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


    def start_loading_secret_game(self):
        self.change_game_state('loading_secret_game')

        # Send the user's username to the socket client (which then forwards it to the server).
        self.client_cmd_queue.put(
            f"!want-play-game:secret_game:{self.client_state.username}:{self.client_state.server_ip}"
        )


    def start_intalling_secret_dlc_game(self):
        if self.client_state.is_already_downloading_dlc:
            print("LOG: already downloading DLC")
            return

        self.client_state.is_already_downloading_dlc = True
        start_getting_dlc(self.secret_dlc_store_update_queue)
