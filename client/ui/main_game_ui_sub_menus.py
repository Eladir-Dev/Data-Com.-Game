# pyright: reportAttributeAccessIssue=false

# This comment disables false-positive Pylance/Pyright errors 
# (related to the `pygame_menu` library) for the entire file.

import pygame
import pygame_menu
from pygame_menu import themes

from common_types.global_state import GlobalClientState, ValidState
from common_types.game_types import SCREEN_WIDTH, SCREEN_HEIGHT
from ui.drawing_utils import apply_ui_scale_pair, apply_ui_scale_int
from typing import Callable

class MainGameSubMenus:
    def __init__(
        self, 
        client_state: GlobalClientState,
        change_game_state: Callable[[ValidState], None],
        start_loading_stratego_game: Callable[[], None],
        start_loading_word_wolf_game: Callable[[], None],
        start_intalling_secret_dlc_game: Callable[[], None]
    ):
        # Reference to the client state.
        self.client_state = client_state

        # Callbacks.
        self.change_game_state = change_game_state
        self.start_loading_stratego_game = start_loading_stratego_game
        self.start_loading_word_wolf_game = start_loading_word_wolf_game
        self.start_intalling_secret_dlc_game = start_intalling_secret_dlc_game

        # Declare the sub menus.
        self.menus: list[pygame_menu.Menu] = []

        self.title_screen = pygame_menu.Menu('Stratego+Word Golf', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_SOLARIZED)
        self.title_screen.add.text_input('Name: ', default=self.client_state.username, onchange=self.set_username)
        self.title_screen.add.text_input('Server IP: ', default=self.client_state.server_ip, onchange=self.set_server_ip)
        self.title_screen.add.button('Game Select', self.show_game_select_menu)
        self.menus.append(self.title_screen)

        self.title_screen_secret_dlc_button = self.title_screen.add.button('DLC Store', self.show_secret_dlc_store)

        self.title_screen.add.button('Settings', self.show_settings_menu)
        self.title_screen.add.button('Quit', pygame_menu.events.EXIT)

        self.game_select_menu = pygame_menu.Menu('Game Select', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
        self.game_select_menu.add.button('Stratego', self.show_deck_selection)
        self.game_select_menu.add.button('Word Golf', self.show_word_golf_menu)
        self.menus.append(self.game_select_menu)

        self.stratego_menu = pygame_menu.Menu('Play Stratego', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
        self.stratego_menu.add.button('Find Match', self.start_loading_stratego_game)
        self.stratego_menu.add.button('Local Game', lambda: print("LOG: hosting Stratego games is not implemented"))
        self.menus.append(self.stratego_menu)

        self.loading_window_stratego = pygame_menu.Menu('Stratego', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
        self.loading_window_stratego.add.label('Connecting...')
        self.menus.append(self.loading_window_stratego)

        self.word_golf_menu = pygame_menu.Menu('Play Word Golf', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
        self.word_golf_menu.add.button('Find Game', self.start_loading_word_wolf_game)
        self.word_golf_menu.add.button('Local Game', lambda: print("LOG: hosting Word Golf games is not implemented"))
        self.menus.append(self.word_golf_menu)

        self.loading_window_word_golf = pygame_menu.Menu('Word Golf', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
        self.loading_window_word_golf.add.label('Connecting...')
        self.menus.append(self.loading_window_word_golf)

        self.loading_window_secret_game = pygame_menu.Menu('Secret Game', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
        self.loading_window_secret_game.add.label('Connecting...')
        self.menus.append(self.loading_window_secret_game)

        self.game_over_menu = pygame_menu.Menu('Game Over', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_SOLARIZED)
        self.game_over_menu.add.label('PLACEHOLDER TEXT', 'game_over_label')
        self.game_over_menu.add.button('Go To Main Menu', self.on_exit_game_over_menu)
        self.game_over_menu.add.button('Quit', pygame_menu.events.EXIT)
        self.menus.append(self.game_over_menu)

        self.secret_dlc_store_menu = pygame_menu.Menu('DLC Store', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_GREEN)
        self.secret_dlc_store_menu.add.button('Play Secret Game', self.start_intalling_secret_dlc_game)
        self.secret_dlc_store_download_progress_bar = self.secret_dlc_store_menu.add.progress_bar('Download Status: ', 0.0)
        self.menus.append(self.secret_dlc_store_menu)

        self.settings_menu = pygame_menu.Menu('Settings Menu', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
        self.settings_menu.add.selector(
            'UI Scale: ', 
            [('Default (x1 size)', 1.0), ('Small (x0.5 size)', 0.5), ('Medium (x1.5 size)', 1.5), ('Large (x2 size)', 2.0)], 
            onchange=lambda _, value: self.set_ui_scale(value),
        )
        self.settings_menu.add.range_slider(
            'Volume: ',
            default=100,
            range_values=(0, 100),
            increment=1,
            onchange=lambda value: self.set_volume(value),
        )
        self.settings_menu.add.button(
            'Apply Changes',
            lambda: self.apply_settings_changes(),
        )
        self.menus.append(self.settings_menu)

        self.arrow = pygame_menu.widgets.LeftArrowSelection(arrow_size=(10, 15))


    def general_update(self):
        self.secret_dlc_store_download_progress_bar.set_value(int(self.client_state.secret_dlc_download_percentage * 100))

        if self.client_state.can_see_secret_dlc_store:
            self.title_screen_secret_dlc_button.show()
        else:
            self.title_screen_secret_dlc_button.hide()


    def on_exit_game_over_menu(self):
        if self.client_state.lore_state is None:
            self.change_game_state('main_menu')

        else:
            self.change_game_state('in_lore')


    def set_username(self, new_username: str):
        self.client_state.username = new_username


    def set_server_ip(self, new_ip: str):
        self.client_state.server_ip = new_ip


    def show_game_select_menu(self):
        self.title_screen._open(self.game_select_menu)


    def show_settings_menu(self):
        self.title_screen._open(self.settings_menu)


    def show_stratego_menu(self):
        self.game_select_menu._open(self.stratego_menu)


    def show_deck_selection(self):
        self.change_game_state("in_deck_selection_state")


    def show_word_golf_menu(self):
        self.game_select_menu._open(self.word_golf_menu)

    
    def show_secret_dlc_store(self):
        self.change_game_state('in_secret_dlc_store')


    def set_ui_scale(self, value: float):
        self.client_state.pending_ui_scale = value


    def set_volume(self, value: float):
        self.client_state.pending_volume = value


    def apply_settings_changes(self):
        self.client_state.ui_scale = self.client_state.pending_ui_scale
        self.client_state.volume = self.client_state.pending_volume

        pygame.display.set_mode(apply_ui_scale_pair((SCREEN_WIDTH, SCREEN_HEIGHT), self.client_state.ui_scale))
        pygame.mixer.music.set_volume(self.client_state.volume / 100)

        self.apply_scale_to_all_submenus()


    def apply_scale_to_all_submenus(self):
        for menu in self.menus:
            menu.resize(
                apply_ui_scale_int(SCREEN_WIDTH, self.client_state.ui_scale),
                apply_ui_scale_int(SCREEN_HEIGHT, self.client_state.ui_scale),
            )


    def set_game_over_message(self, game_over_message: str):
        label = self.game_over_menu.get_widget('game_over_label')
        assert label
        label.set_title(game_over_message)

