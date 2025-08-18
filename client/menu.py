# ================================================================+
# Started on:  April 30, 2025                                     |
# Finished on: _______                                            |
# Programmed by: Eduardo J. Matos                                 |
# Collaborators:                                                  |
#       * Eduardo J Matos Pérez                                   |
#       * Guillermo Myers                                         |
# ----------------------------------------------------------------+
# Description:                                                    |
#      This code creates a menu.                                  |
# ----------------------------------------------------------------+
# Last modification [May 23, 2025]:                               |
#    * Se añadio el codigo encontrado en una pagina de tutorial   |
#                                                                 |
# ================================================================+

# Codigo original del tutorial "Create Menu Screens in Pygame (Tutorial)"
#   Link- https://coderslegacy.com/python/create-menu-screens-in-pygame-tutorial/

# Nota: Este codigo sera modificado, se copio el codigo del tutorial para aprender
#       como funcion y poder crear un menu para el juego

#==========================Imports==========================#
from time import sleep
import pygame
import pygame_menu
from pygame_menu import themes

pygame.init()
surface = pygame.display.set_mode((600, 400))

#==========================Methods==========================#
def set_difficulty(value, difficulty):
    print(value)
    print(difficulty)


def start_the_game():
    mainmenu._open(loading)
    pygame.time.set_timer(update_loading, 30)


def level_menu():
    mainmenu._open(level)

#===========================Logic===========================#

# Se declaran los butones del menu y su funcion
mainmenu = pygame_menu.Menu('Welcome', 600, 400, theme=themes.THEME_SOLARIZED)
mainmenu.add.text_input('Name: ', default='username')
mainmenu.add.button('Play', start_the_game)
mainmenu.add.button('Levels', level_menu)
mainmenu.add.button('Quit', pygame_menu.events.EXIT)

# Se declara el sub menu
level = pygame_menu.Menu('Select a Difficulty', 600, 400, theme=themes.THEME_BLUE)
level.add.selector('Difficulty :', [('Hard', 1), ('Easy', 2)], onchange=set_difficulty)

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
            progress.set_value(progress.get_value() + 1)
            if progress.get_value() == 100:
                pygame.time.set_timer(update_loading, 0)
        if event.type == pygame.QUIT:
            exit()

    if mainmenu.is_enabled():
        mainmenu.update(events)
        mainmenu.draw(surface)
        if (mainmenu.get_current().get_selected_widget()):
            arrow.draw(surface, mainmenu.get_current().get_selected_widget())

    pygame.display.update()