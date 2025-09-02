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

from global_state import GlobalClientState, StrategoGlobalState, ValidState
import socket_client
from game_types import SCREEN_WIDTH, SCREEN_HEIGHT, row_col_to_flat_index
import stratego.stratego_types as stratego_types
from stratego.stratego_types import StrategoBoard, ROWS, COLS, StrategoMoveResult, assert_str_is_color
import stratego.stratego_game as stratego_game

#=======================Client conection====================#
SOCKET_SERVER_CMD_QUEUE: queue.Queue[str] = queue.Queue()
SOCKET_CLIENT_QUEUE: queue.Queue[str] = queue.Queue()

SOCKET_CLIENT_THREAD = threading.Thread(target=socket_client.connect, args=(SOCKET_SERVER_CMD_QUEUE, SOCKET_CLIENT_QUEUE))
SOCKET_CLIENT_THREAD.daemon = True # Allows the program to exit even if the thread is running.
SOCKET_CLIENT_THREAD.start()

GLOBAL_STATE = GlobalClientState(username="johndoe", game_state='main_menu')

def change_game_state(new_state: ValidState):
    """
    Changes the game's state. Used to determine the screen that is being shown.
    """
    GLOBAL_STATE.game_state = new_state


def start():
    pygame.init()
    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    #==========================UI Methods=======================#
    def set_difficulty(value, difficulty):
        print(value)
        print(difficulty)


    def set_username(new_username):
        GLOBAL_STATE.username = new_username

    
    def show_game_select_menu():
        main_menu._open(game_select_menu)


    def show_settings_menu():
        main_menu._open(settings_menu)


    def show_stratego_menu():
        game_select_menu._open(stratego_menu)


    def start_loading_stratego_game():
        # TODO: Send an actual deck customized by the player.
        placeholder_deck = stratego_types.temp_generate_placeholder_deck()

        change_game_state('loading_stratego_game')

        # Send the user's username and starting deck to the socket client (which then forwards it to the server).
        SOCKET_CLIENT_QUEUE.put(
            f"!want-play-game:stratego:{GLOBAL_STATE.username}:{stratego_types.deck_to_socket_message_repr(placeholder_deck)}"
        )


    def show_word_golf_menu():
        game_select_menu._open(word_golf_menu)


    def start_loading_word_wolf_game():
        change_game_state('loading_word_golf_game')

        # Send the user's username to the socket client (which then forwards it to the server).
        SOCKET_CLIENT_QUEUE.put(
            f"!want-play-game:word_golf:{GLOBAL_STATE.username}"
        )


    def host_stratego_game_menu():
        """
        This method opens the (Stratego) host game menu.
        """
        # TODO hacer que funcione bien :)
        pass


    def host_word_golf_menu():
        """
        This method opens the (Word Golf) host game menu.
        """
        # TODO: everything
        pass


    #===========================Logic===========================#

    # Se declaran los butones del menu y su funcion
    main_menu = pygame_menu.Menu('Stratego+Word Golf', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_SOLARIZED)
    main_menu.add.text_input('Name: ', default=GLOBAL_STATE.username, onchange=set_username)
    main_menu.add.button('Game Select', show_game_select_menu)
    main_menu.add.button('Settings', show_settings_menu)
    main_menu.add.button('Quit', pygame_menu.events.EXIT)

    game_select_menu = pygame_menu.Menu('Game Select', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
    game_select_menu.add.button('Stratego', show_stratego_menu)
    game_select_menu.add.button('Word Golf', show_word_golf_menu)

    stratego_menu = pygame_menu.Menu('Play Stratego', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
    stratego_menu.add.button('Find Match', start_loading_stratego_game)
    stratego_menu.add.button('Local Game', host_stratego_game_menu)

    loading_window_stratego = pygame_menu.Menu('Stratego', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
    loading_window_stratego.add.label('Connecting...')

    stratego_game_over_menu = pygame_menu.Menu('Stratego Game Over', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_SOLARIZED)
    stratego_game_over_menu.add.label('PLACEHOLDER TEXT', 'stratego_game_over_label')
    stratego_game_over_menu.add.button('Go To Main Menu', lambda: change_game_state('main_menu'))
    stratego_game_over_menu.add.button('Quit', pygame_menu.events.EXIT)

    word_golf_menu = pygame_menu.Menu('Play Word Golf', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
    word_golf_menu.add.button('Find Game', start_loading_word_wolf_game)
    word_golf_menu.add.button('Local Game', host_word_golf_menu)

    loading_window_word_golf = pygame_menu.Menu('Word Golf', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_BLUE)
    loading_window_word_golf.add.label('Connecting...')

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

                GLOBAL_STATE.stratego_state = StrategoGlobalState(
                    own_color=assert_str_is_color(own_color),
                    own_username=GLOBAL_STATE.username,
                    opponent_username=opponent_username,
                )
                change_game_state('in_stratego_game')

            elif data.startswith("?turn-info"):
                fields = data.split(':')
                current_turn = fields[1]
                board_repr = ':'.join(fields[2:])

                assert GLOBAL_STATE.stratego_state, "Stratego state was None"

                # Update the turn.
                GLOBAL_STATE.stratego_state.turn = current_turn

                # Reset the move result (it no longer needs to be shown, since the board is going 
                # to be reset anyways due to the new turn).
                GLOBAL_STATE.stratego_state.current_move_result = None

                # Update the board with the data from the server.
                board: StrategoBoard = GLOBAL_STATE.stratego_state.board
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

                assert GLOBAL_STATE.stratego_state, "Stratego state was None"

                GLOBAL_STATE.stratego_state.current_move_result = move_result
            

            elif data.startswith("?game-over"):
                fields = data.split(':')
                reason = fields[1]

                if reason == "winner-determined":
                    winning_color = fields[2]
                    game_over_message = f"The ({winning_color}) player has won!"

                elif reason == "abrupt-end":
                    game_over_message = "The game was abruptly ended."

                else:
                    print(f"ERROR: The game unexpectedly ended after server sent `{data}`.")
                    game_over_message = "MISSING GAME OVER MESSAGE"

                label = stratego_game_over_menu.get_widget('stratego_game_over_label')
                assert label
                label.set_title(game_over_message)

                change_game_state('finished_stratego_game')

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

        game_state: ValidState = GLOBAL_STATE.game_state

        if game_state == 'main_menu':
            main_menu.update(events)
            main_menu.draw(surface)
            if (main_menu.get_current().get_selected_widget()):
                arrow.draw(surface, main_menu.get_current().get_selected_widget())

        elif game_state == 'in_stratego_game':
            assert GLOBAL_STATE.stratego_state, "Stratego state was None"

            # Display Stratego game window.
            move_cmd = stratego_game.stratego_update(events, surface, GLOBAL_STATE.stratego_state)

            if move_cmd is not None:
                SOCKET_CLIENT_QUEUE.put(move_cmd)

        elif game_state == 'loading_stratego_game':
            loading_window_stratego.update(events)
            loading_window_stratego.draw(surface)

        elif game_state == 'finished_stratego_game':
            stratego_game_over_menu.update(events)
            stratego_game_over_menu.draw(surface)

        elif game_state == 'in_word_golf_game':
            print("ERROR: word_golf game is not implemented yet")

        elif game_state == 'loading_word_golf_game':
            loading_window_word_golf.update(events)
            loading_window_word_golf.draw(surface)

        elif game_state == 'finished_word_golf_game':
            print("ERROR: word_golf is not implemented yet")

        else:
            print(f"ERROR: unhandled game state '{game_state}'")

        pygame.display.update()
