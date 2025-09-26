# pyright: reportAttributeAccessIssue=false

from typing import Callable
import pygame
from pygame import Surface
from pygame.event import Event
import pygame_menu
import random

from pygame_menu.widgets.core import Selection

#import stratego_types as stratego_types
from . import stratego_types
#from stratego_types import *
from .stratego_types import StrategoRenderedTile
# from "/stratego_types.py"
# class DeckSelection(pygame_menu.Menu):
from global_state import GlobalClientState

class RedHighlight(Selection):
    """
    Selection widget for when start game is selected and there is no deck selected.
    """
    def __init__(self):
        super().__init__(margin_left=0, margin_right=0, margin_top=0, margin_bottom=0)

    def draw(self, surface, widget):
        # Get widget position and size
        rect = widget.get_rect()
        rect.inflate_ip(10, 10)  # Optional: expand the rectangle slightly

        # Draw red border
        pygame.draw.rect(surface, (255, 0, 0), rect, 3)  # RGB red, thickness 3

class GreenHighlight(Selection):
    """
    Selection widget for when start game is selected and there is no deck selected.
    """
    def __init__(self):
        super().__init__(margin_left=0, margin_right=0, margin_top=0, margin_bottom=0)

    def draw(self, surface, widget):
        # Get widget position and size
        rect = widget.get_rect()
        rect.inflate_ip(10, 10)  # Optional: expand the rectangle slightly

        # Draw red border
        pygame.draw.rect(surface, (0, 255, 0), rect, 3)  # RGB red, thickness 3
        pygame.draw.rect(surface, (144, 238, 144), rect, 1)  # Light green fill (RGB for light green)

class StrategoSettingsWindow():
    def __init__(self, 
        surface: Surface, 
        go_to_prev_menu: Callable[[], None], 
        go_to_start: Callable[[], None], 
        player_data: GlobalClientState,
    ):
        self.surface = surface
        # Methods
        self.go_to_start = go_to_start

        #======================Custom theme======================#
        self.theme = pygame_menu.themes.THEME_DARK.copy()
        self.theme.widget_alignment = pygame_menu.locals.ALIGN_LEFT
        self.theme.title = False  # Optional: hide title
        self.theme.widget_font_size = 25
        # ======================Deck data=========================#
        rows = 10
        cols = 4
        self.username = player_data.username
        self.pieces = [['' for _ in range(rows)] for _ in range(cols)]
        self.deck = [['' for _ in range(rows)] for _ in range(cols)]
        self.fill_pieces(rows, cols, True)

        # Create menu with left-side layout
        menu_hight = 600
        self.menu = pygame_menu.Menu(
            height=menu_hight,
            width=275,  # Sidebar width
            title='Game Options',
            theme=self.theme,
            center_content=False  # Disable auto-centering
        )
        self.menu.set_relative_position(0, 10)
        # Add widgets with manual positioning
        self.menu.add.label('==Game Options==', float=True).translate(5, 35)
        button_spacing = 60
        self.menu.add.text_input('Name: ', default=self.username, float=True).translate(20, 100)
        self.start_button = self.menu.add.button('Start Game', self.start_game, float=True).translate(20, 100 + button_spacing)
        self.menu.add.button('Random Deck', lambda: self.set_rand_deck(player_data), float=True).translate(20, 100 + button_spacing * 2)
        self.menu.add.selector('Timer:  ', [('On', 1), ('Off', 2)], float=True).translate(20, 100 + button_spacing * 3)
        self.menu.add.button('<- Return', go_to_prev_menu, float=True).translate(20, menu_hight - 60)

        #red highlight for start_button
        red_selection = RedHighlight()
        self.start_button.set_selection_effect(red_selection)


    def deck_full(self):
        """
        This method verifies if the deck is full.
        """
        for row in range(len(self.deck)):
            for col in range(len(self.deck[row])):
                if self.deck[row][col] == '':
                    return False
        return True

    def start_game(self):
        """
        This method starts the game.
        """
        if self.deck_full():
            self.go_to_start()

    def fill_pieces(self, rows, cols,debug):
        """
        This method fills the pieces array were the player selects his deck.
        """
        """
        Encoding legend:
        * 'S' = Spy (1)
        * '1' = Marshal (1)
        * 'G' = General (1)
        * '2' = Coronel (2)
        * '3' = Major (3)
        * 'C' = Captain (4)
        * 'L' = Lieutenant (4)
        * '4' = Sargeant (4)
        * '8' = Scout (8)
        * '5' = Miner (5)
        * 'B' = Bomb (6)
        * 'F' = Flag (1)
        """
        limits = {
            'S': 1,
            '1': 1,
            'G': 1,
            '2': 2,
            '3': 3,
            'C': 4,
            'L': 4,
            '4': 4,
            '8': 8,
            '5': 5,
            'B': 6,
            'F': 1
        }

        # Create the deck (2D array)
        deck = [['' for _ in range(10)] for _ in range(4)]

        # Flatten the deck for easier filling
        flat_deck = [cell for row in deck for cell in row]

        # Create a list of items to fill the deck based on limits
        items_to_fill = []
        for item, limit in limits.items():
            items_to_fill.extend([item] * limit)

        # Fill the deck
        for i in range(len(flat_deck)):
            if i < len(items_to_fill):
                flat_deck[i] = items_to_fill[i]

        # Convert the flat deck back to 2D
        for i in range(4):
            for j in range(10):
                self.pieces[i][j] = flat_deck[i * 10 + j]
        #
        # unitAmountIdx = 0
        # # unit[piece, amount]
        # units = [('S', 1), ('1', 1), ('G', 1), ('2', 2), ('3', 3), ('C', 4), ('L', 4), ('4', 4), ('8', 8), ('5', 5),
        #          ('B', 6), ('F', 1)]
        # acum = 0
        # for col in range(cols):  # creats the 2d array TODO todavia no esta terminado
        #     for row in range(rows):
        #         unit = units[unitAmountIdx]
        #         amount = unit[1]
        #         if (amount - acum) <= 0:
        #             unitAmountIdx += 1
        #             acum = 0
        #             unit = units[unitAmountIdx]
        #
        #             if debug:
        #                 print(col, row)
        #             self.pieces[col][row] = unit[0]  # adds string to 2d array
        #             acum = acum + 1
        #
        #         else:
        #             if debug:
        #                 print(col, row)
        #             self.pieces[col][row] = unit[0]  # adds string to 2d array
        #             acum = acum + 1
        if debug:
            for col in range(cols):
                print(self.pieces[col])

    def create_random_deck(self):
        """
          This method creats a random deck
          Parameters:
            Output:
              deck (2D array)
        """

        # limits = {
        #     's': 1,
        #     '1': 8,
        #     '2': 5,
        #     '3': 4,
        #     '4': 4,
        #     '5': 4,
        #     '6': 3,
        #     '7': 2,
        #     '8': 1,
        #     '9': 1,
        #     'b': 6,
        #     'f': 1
        # }

        limits = {
            'S': 1,
            '1': 1,
            'G': 1,
            '2': 2,
            '3': 3,
            'C': 4,
            'L': 4,
            '4': 4,
            '8': 8,
            '5': 5,
            'B': 6,
            'F': 1
        }

        # Create the deck (2D array)
        deck = [['' for _ in range(10)] for _ in range(4)]

        # Flatten the deck for easier filling
        flat_deck = [cell for row in deck for cell in row]

        # Create a list of items to fill the deck based on limits
        items_to_fill = []
        for item, limit in limits.items():
            items_to_fill.extend([item] * limit)

        # Shuffle the items to randomize their placement
        random.shuffle(items_to_fill)

        # Fill the deck
        for i in range(len(flat_deck)):
            if i < len(items_to_fill):
                flat_deck[i] = items_to_fill[i]

        # Convert the flat deck back to 2D
        for i in range(4):
            for j in range(10):
                deck[i][j] = flat_deck[i * 10 + j]

        return deck

    def set_rand_deck(self, global_data: GlobalClientState):
        """
        This method sets the random deck.
        """
        self.deck = self.create_random_deck()
        self.empty_pieces()
        flattened_deck = stratego_types.flatten_2d_array(self.deck)
        global_data.stratego_starting_deck_repr = stratego_types.deck_to_socket_message_repr(flattened_deck)


    def empty_pieces(self):
        """
        This method empties the array of pieces from were the player selects his deck
        """
        for row in range(len(self.pieces)):
            for col in range(len(self.pieces[row])):
                self.pieces[row][col] = ''

    def main(self):
        while True:
            events = pygame.event.get()
            self.update(events)

        #self.__init__()# TODO revisar coo mejora y si todo esta bien
        #game_settings = self.generate_screen()
        #Main loop
        # while True:
        #     events = pygame.event.get()
        #     for event in events:
        #         if event.type == pygame.QUIT:
        #             exit()
        #
        #     surface.fill((50, 50, 50))  # Background
        #
        #     # You can draw other UI elements here (e.g., game canvas on the right)
        #     pygame.draw.rect(surface, (100, 100, 200), (300, 50, 575, 500))  # Example UI panel
        #
        #     game_settings.menu.update(events)
        #     game_settings.menu.draw(surface)
        #     pygame.display.flip()
        # events = pygame.event.get()
        # for event in events:
        #     if event.type == pygame.MOUSEBUTTONDOWN:
        #         mouse_pos = event.pos

        #         print(mouse_pos)

        #         for rendered_tile in rendered_tiles:
        #             sprite_rect = rendered_tile.sprite_rect

        #             if sprite_rect.collidepoint(mouse_pos):
        #                 # TODO: Do not print these out in an actual game, it
        #                 # would ruin the entire point of hiding the opponent's pieces.
        #                 print(rendered_tile.str_encoding)

        #                 if global_game_data.last_selected_piece is None:
        #                     # Select the tile.
        #                     global_game_data.last_selected_piece = rendered_tile

        #                 else:
        #                     from_pos = global_game_data.last_selected_piece.board_location
        #                     to_pos = rendered_tile.board_location

        #                     move_cmd = gen_move_cmd(from_pos, to_pos)

        #                     # Un-select the tile.
        #                     global_game_data.last_selected_piece = None
            #You can draw other UI elements here (e.g., game canvas on the right)


    def update(self, events: list[Event]):
        """
        Updates the UI.
        """
        # Draw the UI.
        pygame.draw.rect(self.surface, (100, 100, 200), (300, 50, 575, 500))  # Example UI panel

        if self.deck_full():
            green_selection = GreenHighlight()
            self.start_button.set_selection_effect(green_selection)

        self.menu.update(events)
        self.menu.draw(self.surface)
        pygame.display.flip()




def main():
    pygame.init()
    surface = pygame.display.set_mode((900, 600))

    # game_settings = GameSettings(surface)
    # game_settings.main()

if __name__ == "__main__":
   main()