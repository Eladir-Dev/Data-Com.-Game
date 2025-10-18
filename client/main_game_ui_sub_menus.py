# pyright: reportAttributeAccessIssue=false

# This comment disables false-positive Pylance/Pyright errors 
# (related to the `pygame_menu` library) for the entire file.

import pygame
import pygame_menu
from pygame_menu import themes

from global_state import GlobalClientState, ValidState
from game_types import SCREEN_WIDTH, SCREEN_HEIGHT
from typing import Callable

class MainGameSubMenus:
    def __init__(
        self, 
        client_state: GlobalClientState,
        change_game_state: Callable[[ValidState], None],
        start_loading_stratego_game: Callable[[], None],
        start_loading_word_wolf_game: Callable[[], None],
    ):
        # Reference to the client state.
        self.client_state = client_state

        # Callbacks.
        self.change_game_state = change_game_state
        self.start_loading_stratego_game = start_loading_stratego_game
        self.start_loading_word_wolf_game = start_loading_word_wolf_game

        # Declare the sub menus.
        self.title_screen = pygame_menu.Menu('Stratego+Word Golf', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_SOLARIZED)
        self.title_screen.add.text_input('Name: ', default=self.client_state.username, onchange=self.set_username)
        self.title_screen.add.text_input('Server IP: ', default=self.client_state.server_ip, onchange=self.set_server_ip)
        self.title_screen.add.button('Game Select', self.show_game_select_menu)
        self.title_screen.add.button('Settings', self.show_settings_menu)
        self.title_screen.add.button('Quit', pygame_menu.events.EXIT)

        self.game_select_menu = pygame_menu.Menu('Game Select', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
        self.game_select_menu.add.button('Stratego', self.show_deck_selection)
        self.game_select_menu.add.button('Word Golf', self.show_word_golf_menu)

        self.stratego_menu = pygame_menu.Menu('Play Stratego', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
        self.stratego_menu.add.button('Find Match', self.start_loading_stratego_game)
        self.stratego_menu.add.button('Local Game', lambda: print("LOG: hosting Stratego games is not implemented"))

        self.loading_window_stratego = pygame_menu.Menu('Stratego', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
        self.loading_window_stratego.add.label('Connecting...')

        self.word_golf_menu = pygame_menu.Menu('Play Word Golf', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
        self.word_golf_menu.add.button('Find Game', self.start_loading_word_wolf_game)
        self.word_golf_menu.add.button('Local Game', lambda: print("LOG: hosting Word Golf games is not implemented"))

        self.loading_window_word_golf = pygame_menu.Menu('Word Golf', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
        self.loading_window_word_golf.add.label('Connecting...')

        self.game_over_menu = pygame_menu.Menu('Game Over', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_SOLARIZED)
        self.game_over_menu.add.label('PLACEHOLDER TEXT', 'game_over_label')
        self.game_over_menu.add.button('Go To Main Menu', self.go_to_main_menu)
        self.game_over_menu.add.button('Quit', pygame_menu.events.EXIT)

        self.settings_menu = pygame_menu.Menu('Settings Menu', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
        self.settings_menu.add.selector('Difficulty (This is a placeholder setting TO BE REMOVED) :', [('Hard', 1), ('Easy', 2)], onchange=lambda: "LOG: difficulty slider to be removed")

        self.loading = pygame_menu.Menu('Loading the Game...', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_DARK)
        self.loading.add.progress_bar("Progress", progressbar_id="1", default=0, width=200, )

        self.arrow = pygame_menu.widgets.LeftArrowSelection(arrow_size=(10, 15))

        self.update_loading = pygame.USEREVENT + 0


    def go_to_main_menu(self):
        self.change_game_state('main_menu')


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