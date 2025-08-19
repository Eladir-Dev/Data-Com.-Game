# pyright: reportAttributeAccessIssue=false
# This comment disables false-positive Pylance/Pyright errors for the entire file.

#==========================Imports==========================#
# from time import sleep
import pygame
import pygame_menu
from pygame_menu import themes

GLOBALS = {
    "username": "johndoe"
}

def start():
    pygame.init()
    surface = pygame.display.set_mode((600, 400))

    #==========================UI Methods=======================#
    def set_difficulty(value, difficulty):
        print(value)
        print(difficulty)


    def set_username(new_username):
        GLOBALS['username'] = new_username
        print(GLOBALS['username'])

    
    def show_game_select_menu():
        main_menu._open(game_select_menu)


    def show_settings_menu():
        main_menu._open(settings_menu)


    def show_stratego_menu():
        game_select_menu._open(stratego_menu)


    def show_loading_window_stratego():
        # TODO: Figure out how to remove back button or change the main menu.
        main_menu._open(loading_window_stratego)


    def show_wordle_menu():
        game_select_menu._open(wordle_menu)
    

    #===========================Logic===========================#

    # Se declaran los butones del menu y su funcion
    main_menu = pygame_menu.Menu('Stratego+Wordle', 600, 400, theme=themes.THEME_SOLARIZED)
    main_menu.add.text_input('Name: ', default=GLOBALS['username'], onchange=set_username)
    main_menu.add.button('Game Select', show_game_select_menu)
    main_menu.add.button('Settings', show_settings_menu)
    main_menu.add.button('Quit', pygame_menu.events.EXIT)

    game_select_menu = pygame_menu.Menu('Game Select', 600, 400, theme=themes.THEME_BLUE)
    game_select_menu.add.button('Stratego', show_stratego_menu)
    game_select_menu.add.button('Wordle', show_wordle_menu)

    stratego_menu = pygame_menu.Menu('Play Stratego', 600, 400, theme=themes.THEME_BLUE)
    stratego_menu.add.button('Find Match', show_loading_window_stratego)

    loading_window_stratego = pygame_menu.Menu('Play Stratego', 600, 400, theme=themes.THEME_BLUE)
    loading_window_stratego.add.label('Loading...')

    wordle_menu = pygame_menu.Menu('Play Wordle', 600, 400, theme=themes.THEME_BLUE)
    wordle_menu.add.label('TODO')

    # Se declara el sub menu
    settings_menu = pygame_menu.Menu('Settings Menu', 600, 400, theme=themes.THEME_BLUE)
    settings_menu.add.selector('Difficulty (This is a placeholder setting TO BE REMOVED) :', [('Hard', 1), ('Easy', 2)], onchange=set_difficulty)

    # se declara la pantalla de carga
    loading = pygame_menu.Menu('Loading the Game...', 600, 400, theme=themes.THEME_DARK)
    loading.add.progress_bar("Progress", progressbar_id="1", default=0, width=200, )

    # se declara la flechita
    arrow = pygame_menu.widgets.LeftArrowSelection(arrow_size=(10, 15))

    update_loading = pygame.USEREVENT + 0

    # ciclo del juego
    while True:
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

        if main_menu.is_enabled():
            main_menu.update(events)
            main_menu.draw(surface)
            if (main_menu.get_current().get_selected_widget()):
                arrow.draw(surface, main_menu.get_current().get_selected_widget())

        pygame.display.update()