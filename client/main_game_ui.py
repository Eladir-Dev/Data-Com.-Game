# pyright: reportAttributeAccessIssue=false
# This comment disables false-positive Pylance/Pyright errors for the entire file.

#==========================Imports==========================#
# from time import sleep
import pygame
import pygame_menu
from pygame_menu import themes
from typing import Literal
import queue
import threading

import socket_client
from game_types import SCREEN_WIDTH, SCREEN_HEIGHT, row_col_to_flat_index
import stratego.stratego_types as stratego_types
from stratego.stratego_types import Board, ROWS, COLS
import stratego.stratego_display as stratego_display

#=======================Client conection====================#
SOCKET_SERVER_CMD_QUEUE: queue.Queue[str] = queue.Queue()
SOCKET_CLIENT_QUEUE: queue.Queue[str] = queue.Queue()

SOCKET_CLIENT_THREAD = threading.Thread(target=socket_client.connect, args=(SOCKET_SERVER_CMD_QUEUE, SOCKET_CLIENT_QUEUE))
SOCKET_CLIENT_THREAD.daemon = True # Allows the program to exit even if the thread is running.
SOCKET_CLIENT_THREAD.start()

# TODO: This global state object can be cleaned up into a proper class.
# The Stratego state objects definitely need to be re-organized. It is awkward tha the username 
# is in a different spot than the rest of the Stratego stuff and different than the `StrategoPlayerInfo` 
# used by the `socket_client` module.
GLOBALS = {
    "username": "johndoe",
    'state': "main_menu",
    'stratego_state': None,
}

ValidState = Literal['main_menu', 'in_stratego_game', 'in_wordle_game']


def change_game_state(new_state: ValidState):
    """
    Changes the game's state. Used to determine the screen that is being shown.
    """
    GLOBALS['state'] = new_state


def start():
    pygame.init()
    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    #==========================UI Methods=======================#
    def set_difficulty(value, difficulty):
        print(value)
        print(difficulty)


    def set_username(new_username):
        GLOBALS['username'] = new_username

    
    def show_game_select_menu():
        main_menu._open(game_select_menu)


    def show_settings_menu():
        main_menu._open(settings_menu)


    def show_stratego_menu():
        game_select_menu._open(stratego_menu)


    def show_loading_window_stratego():
        # TODO: Figure out how to remove back button or change the main menu.
        main_menu._open(loading_window_stratego)

        # TODO: Send an actual deck customized by the player.
        placeholder_deck = stratego_types.temp_generate_placeholder_deck()

        SOCKET_CLIENT_QUEUE.put(
            f"!want-play-game:stratego:{GLOBALS['username']}:{stratego_types.deck_to_socket_message_repr(placeholder_deck)}"
        )


    def show_wordle_menu():
        game_select_menu._open(wordle_menu)


    def host_game_menu():
        """
        This method opens the host game menu
        """
        # TODO hacer que funcione bien :)
        pass
    

    #===========================Logic===========================#

    # Se declaran los butones del menu y su funcion
    main_menu = pygame_menu.Menu('Stratego+Wordle', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_SOLARIZED)
    main_menu.add.text_input('Name: ', default=GLOBALS['username'], onchange=set_username)
    main_menu.add.button('Game Select', show_game_select_menu)
    main_menu.add.button('Settings', show_settings_menu)
    main_menu.add.button('Quit', pygame_menu.events.EXIT)

    game_select_menu = pygame_menu.Menu('Game Select', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
    game_select_menu.add.button('Stratego', show_stratego_menu)
    game_select_menu.add.button('Wordle', show_wordle_menu)

    stratego_menu = pygame_menu.Menu('Play Stratego', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
    stratego_menu.add.button('Find Match', show_loading_window_stratego)
    stratego_menu.add.button('Local Game', host_game_menu)

    loading_window_stratego = pygame_menu.Menu('Stratego', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
    loading_window_stratego.add.label('Connecting...')

    wordle_menu = pygame_menu.Menu('Play Wordle', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
    wordle_menu.add.label('TODO')

    # Se declara el sub menu
    settings_menu = pygame_menu.Menu('Settings Menu', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
    settings_menu.add.selector('Difficulty (This is a placeholder setting TO BE REMOVED) :', [('Hard', 1), ('Easy', 2)], onchange=set_difficulty)

    # se declara la pantalla de carga
    loading = pygame_menu.Menu('Loading the Game...', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_DARK)
    loading.add.progress_bar("Progress", progressbar_id="1", default=0, width=200, )

    # se declara la flechita
    arrow = pygame_menu.widgets.LeftArrowSelection(arrow_size=(10, 15))

    update_loading = pygame.USEREVENT + 0

    # ciclo del juego
    while True:
        while not SOCKET_SERVER_CMD_QUEUE.empty():
            data = SOCKET_SERVER_CMD_QUEUE.get()

            if data.startswith("?game-start"):
                fields = data.split(':')
                own_color = fields[1]
                opponent_username = fields[2]

                GLOBALS['stratego_state'] = {
                    'own_color': own_color,
                    'opponent_username': opponent_username,
                    # Empty board; gets filled in each turn with info from the server.
                    'board': Board(), 
                    # The red player always goes first.
                    'turn': 'r',
                }
                change_game_state('in_stratego_game')
                # Does this .disable() do anything here?
                main_menu.disable()

            elif data.startswith("?turn-info"):
                fields = data.split(':')
                current_turn = fields[1]
                board_repr = ':'.join(fields[2:])

                # Update the turn.
                GLOBALS['stratego_state']['turn'] = current_turn

                # Update the board with the data from the server.
                board: Board = GLOBALS['stratego_state']['board']
                board.update_elements_with_socket_repr(board_repr)

                # TEMP: Check current state.
                print(GLOBALS)

                print(f"=== BOARD ===")


                # TODO: This is temporary.
                # However, similar logic will be added to the `stratego_display` module 
                # for displaying the board on the actual UI.

                # The ranges need to be lambdas since ranges (like all generators) are 
                # mutable. If stored in a variable and used, they will be exhausted by the 
                # time of the next loop iteration, causing unexpected behavior.
                # This is resolved with the use of a lambda, which returns a new range 
                # each time it's called.
                if GLOBALS['stratego_state']['own_color'] == 'r':
                    get_row_range = lambda: range(ROWS)
                    get_col_range = lambda: range(COLS)
                
                else:
                    # Return reversed ranges to view the board at a 180 degree view.
                    get_row_range = lambda: reversed(range(ROWS))
                    get_col_range = lambda: reversed(range(COLS))

                times = 0
                for r in get_row_range():
                    for c in get_col_range():
                        flat_idx = row_col_to_flat_index(r, c, COLS)
                        print(f"{board.elements[flat_idx]} ", end='')

                        times += 1
                    
                    print()

                print(f"Printed {times} board elements")

            else:
                print(f"ERROR: Unknown server command: '{data}'")

        events = pygame.event.get()
        for event in events:
            if event.type == update_loading:
                progress = loading.get_widget("1")
                assert progress # fixes null errors; crashes if progress is somehow `None`

                progress.set_value(progress.get_value() + 1)
                if progress.get_value() == 100:
                    pygame.time.set_timer(update_loading, 0)
            if event.type == pygame.QUIT:
                exit()

        game_state: ValidState = GLOBALS['state']

        if game_state == 'main_menu':
            if main_menu.is_enabled():
                main_menu.update(events)
                main_menu.draw(surface)
                if (main_menu.get_current().get_selected_widget()):
                    arrow.draw(surface, main_menu.get_current().get_selected_widget())

        elif game_state == 'in_stratego_game':
            # Display Stratego game window.
            stratego_display.stratego_update(events, surface, GLOBALS, SOCKET_SERVER_CMD_QUEUE, SOCKET_CLIENT_QUEUE)

        elif game_state == 'in_wordle_game':
            print("ERROR: Wordle is not implemented yet")

        pygame.display.update()
