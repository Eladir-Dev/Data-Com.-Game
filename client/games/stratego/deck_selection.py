# pyright: reportAttributeAccessIssue=false
# ================================================================+
# Started on:  September 2, 2025                                  |
# Finished on: November 9, 2025                                   |
# Programmed by: Eduardo J. Matos                                 |
# Collaborators:                                                  |
#       * Eduardo J Matos Pérez                                   |
#       * Guillermo Myers                                         |
# ----------------------------------------------------------------+
# Description:                                                    |
#      This code is responsible for managing the deck selection   |
#      screen for the Stratego game.                              |
# ----------------------------------------------------------------+
# Last modification [November 9, 2025]:                           |
#    * The following methods were added:                          |
#                                                                 |
#    * The following methods were eliminated:                     |
#                                                                 |
#    * Other: The code was cleaned                                |
#                                                                 |
# ================================================================+

#==========================Imports================================#
from ui.drawing_utils import draw_text
from typing import Callable
import pygame
from pygame import Surface
from pygame.event import Event
import pygame_menu
import random
from pygame_menu.widgets.core import Selection


from . import stratego_types
#from stratego_types import *
from .stratego_types import StrategoRenderedTile
from common_types.global_state import GlobalClientState
from common_types.game_types import SCREEN_WIDTH
from pathlib import Path
#=================================================================#
SPRITE_FOLDER = Path(__file__).parent / "assets"
"""Sprite folder address"""

#=========================High Lights=============================#
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
#=================================================================#

class DeckSelector():
    """
    This class take care of drawing the grids for the deck selection.
    """

    def handle_mouse_event(self, event, top_grid, bottom_grid):
        """
        This function handles mouse events when a mouse button is pressed.
        """
        CELL_SIZE = 50
        GRID_COLS = 10
        GRID_ROWS = 4
        TOP_GRID_Y = 70
        BOTTOM_GRID_Y = 340
        X_START = 336

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button down
            mouse_x, mouse_y = event.pos
            # Check if click is in top grid
            if (TOP_GRID_Y <= mouse_y < TOP_GRID_Y + GRID_ROWS * CELL_SIZE and
                X_START <= mouse_x < X_START + GRID_COLS * CELL_SIZE):
                col = (mouse_x - X_START) // CELL_SIZE
                row = (mouse_y - TOP_GRID_Y) // CELL_SIZE
                if top_grid[row][col] != "":  # There's a piece here
                    self.dragging = True
                    self.dragged_piece = top_grid[row][col]
                    self.dragged_from = 'top'
                    self.drag_row = row
                    self.drag_col = col
                    top_grid[row][col] = ""  # Temporarily remove from grid
                    # Calculate offset to center the sprite on the mouse
                    self.drag_offset = (mouse_x - (X_START + col * CELL_SIZE + CELL_SIZE // 2)+20,
                                        mouse_y - (TOP_GRID_Y + row * CELL_SIZE + CELL_SIZE // 2)+30)
            # Check if click is in bottom grid
            elif (BOTTOM_GRID_Y <= mouse_y < BOTTOM_GRID_Y + GRID_ROWS * CELL_SIZE and
                  X_START <= mouse_x < X_START + GRID_COLS * CELL_SIZE):
                col = (mouse_x - X_START) // CELL_SIZE
                row = (mouse_y - BOTTOM_GRID_Y) // CELL_SIZE
                if bottom_grid[row][col] != "":  # There's a piece here
                    self.dragging = True
                    self.dragged_piece = bottom_grid[row][col]
                    self.dragged_from = 'bottom'
                    self.drag_row = row
                    self.drag_col = col
                    bottom_grid[row][col] = ""  # Temporarily remove from grid
                    # Calculate offset to center the sprite on the mouse
                    self.drag_offset = (mouse_x - (X_START + col * CELL_SIZE + CELL_SIZE // 2)+20,
                                        mouse_y - (BOTTOM_GRID_Y + row * CELL_SIZE + CELL_SIZE // 2)+30)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.dragging:  # Left mouse button up
            mouse_x, mouse_y = event.pos
            dropped = False

            # Check if mouse is over bottom grid
            if (BOTTOM_GRID_Y <= mouse_y < BOTTOM_GRID_Y + GRID_ROWS * CELL_SIZE and
                X_START <= mouse_x < X_START + GRID_COLS * CELL_SIZE):
                col = (mouse_x - X_START) // CELL_SIZE
                row = (mouse_y - BOTTOM_GRID_Y) // CELL_SIZE
                if bottom_grid[row][col] == "":  # Only drop if the cell is empty
                    bottom_grid[row][col] = self.dragged_piece
                    dropped = True

            # Check if mouse is over top grid
            if (TOP_GRID_Y <= mouse_y < TOP_GRID_Y + GRID_ROWS * CELL_SIZE and
                X_START <= mouse_x < X_START + GRID_COLS * CELL_SIZE):
                col = (mouse_x - X_START) // CELL_SIZE
                row = (mouse_y - TOP_GRID_Y) // CELL_SIZE
                if top_grid[row][col] == "":  # Only drop if the cell is empty
                    top_grid[row][col] = self.dragged_piece
                    dropped = True
            # If drop failed, return to original position
            if not dropped:
                if self.dragged_from == 'top':
                    top_grid[self.drag_row][self.drag_col] = self.dragged_piece
                else:
                    bottom_grid[self.drag_row][self.drag_col] = self.dragged_piece
            #Reset drag state
            self.dragging = False
            self.dragged_piece = None
            self.dragged_from = None
            self.drag_row = None
            self.drag_col = None
            self.drag_offset = (0, 0)



    def draw(self, surface, top_grid, bottom_grid):
        """
        This function draws the grids and sprites for the Deck selection screen.
        """



        for key in self.sprites:
            self.sprites[key] = pygame.transform.scale(self.sprites[key], (self.CELL_SIZE, self.CELL_SIZE))

        # Constants
        CELL_SIZE = 50
        GRID_COLS = 10
        GRID_ROWS = 4
        TOP_GRID_Y = 70
        BOTTOM_GRID_Y = 340
        X_START = 336
        # Colors
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        CREMA = (219, 196, 156)
        LIGHT_GRAY = (200, 200, 200)
        LIGHT_GRAY2 = 133, 133, 133
        COLORS = [(255, 0, 0), (255, 100, 100), (0, 0, 255), (100, 100, 255), (0, 255, 0), (255, 255, 0),
                  (255, 255, 100), (100, 255, 100), (255, 100, 255), (100, 255, 255)]
        BLUE_BAR = (24, 43, 51)
        GRAY_BACKGROUND = (51, 49, 45)

        pygame.draw.rect(surface, CREMA, (275, 30, 650, 600))  # Background
        pygame.draw.rect(surface, BLUE_BAR, (0, 0, 900, 40))  # Upper bar

        pygame.draw.rect(surface, LIGHT_GRAY2, (0, 40, 900, 3))  # lines

        pygame.draw.rect(surface, (51, 49, 45), (300, 50, 575, 520))  # Grid backgrounds

        # Render main text
        draw_text(surface, "Stratego", 36,(SCREEN_WIDTH//2, 20), (255, 255, 255))


        # Top grid outline: Horizontal/vertical lines for visual slots.
        for row in range(GRID_ROWS + 1):
            y = TOP_GRID_Y + row * CELL_SIZE
            pygame.draw.line(surface, WHITE, (X_START, y), (X_START + GRID_COLS * CELL_SIZE, y), 2)
        for col in range(GRID_COLS + 1):
            x = X_START + col * CELL_SIZE
            pygame.draw.line(surface, WHITE, (x, TOP_GRID_Y), (x, TOP_GRID_Y + GRID_ROWS * CELL_SIZE), 2)

        # Bottom grid outline: Identical to top for consistency.
        for row in range(GRID_ROWS + 1):
            y = BOTTOM_GRID_Y + row * CELL_SIZE
            pygame.draw.line(surface, WHITE, (X_START, y), (X_START + GRID_COLS * CELL_SIZE, y), 2)
        for col in range(GRID_COLS + 1):
            x = X_START + col * CELL_SIZE
            pygame.draw.line(surface, WHITE, (x, BOTTOM_GRID_Y), (x, BOTTOM_GRID_Y + GRID_ROWS * CELL_SIZE), 2)

        # Draw pieces in the top grid based on self.top_grid
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                piece = top_grid[row][col]
                if piece != "":  # Only draw if there's a piece
                    x = X_START + col * CELL_SIZE
                    y = TOP_GRID_Y + row * CELL_SIZE
                    surface.blit(self.sprites[piece], (x, y))  # Blit the sprite at the cell's top-left

        # Draw pieces in the bottom grid based on self.bottom_grid
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                piece = bottom_grid[row][col]
                if piece != "":  # Only draw if there's a piece
                    x = X_START + col * CELL_SIZE
                    y = BOTTOM_GRID_Y + row * CELL_SIZE
                    surface.blit(self.sprites[piece], (x, y))  # Blit the sprite at the cell's top-left

        # If dragging, draw the dragged sprite at the mouse position (centered)
        if self.dragging and self.dragged_piece:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            drag_x = mouse_x - self.drag_offset[0]
            drag_y = mouse_y - self.drag_offset[1]
            surface.blit(self.sprites[self.dragged_piece], (drag_x, drag_y))

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
        self.go_to_prev_menu = go_to_prev_menu

        self.st_custom_game_menu = None
        self.in_custom_game = False

        #======================Custom theme======================#
        self.theme = pygame_menu.themes.THEME_DARK.copy()
        self.theme.widget_alignment = pygame_menu.locals.ALIGN_LEFT
        self.theme.title = False  # Optional: hide title
        self.theme.widget_font_size = 25
        # ======================Deck data=========================#
        rows = 10
        cols = 4
        self.player_data = player_data
        self.pieces = [['' for _ in range(rows)] for _ in range(cols)]
        self.deck = [['' for _ in range(rows)] for _ in range(cols)]
        self.fill_pieces(rows, cols, True)
        # ====================Deck renderer========================#
        # Drag-and-drop state variables
        self.dragging = False
        self.dragged_piece = None
        self.dragged_from = None  # 'top' or 'bottom'
        self.drag_row = None
        self.drag_col = None
        self.drag_offset = (0, 0)  # Offset to center the sprite on the mouse
        self.CELL_SIZE = 50
        # Sprite addreses
        self.sprites = {
            "S": pygame.image.load(f"{SPRITE_FOLDER}/red_spy.png"),  # Replace with real paths
            "1": pygame.image.load(f"{SPRITE_FOLDER}/red_marshal.png"),
            "G": pygame.image.load(f"{SPRITE_FOLDER}/red_general.png"),
            "2": pygame.image.load(f"{SPRITE_FOLDER}/red_coronel.png"),
            "3": pygame.image.load(f"{SPRITE_FOLDER}/red_major.png"),
            "C": pygame.image.load(f"{SPRITE_FOLDER}/red_captain.png"),
            "L": pygame.image.load(f"{SPRITE_FOLDER}/red_lieutenant.png"),
            "4": pygame.image.load(f"{SPRITE_FOLDER}/red_sergeant.png"),
            "8": pygame.image.load(f"{SPRITE_FOLDER}/red_scout.png"),
            "5": pygame.image.load(f"{SPRITE_FOLDER}/red_miner.png"),
            "B": pygame.image.load(f"{SPRITE_FOLDER}/red_bomb.png"),
            "F": pygame.image.load(f"{SPRITE_FOLDER}/red_flag.png"),
        }
        # =========================================================#

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
        self.label = self.menu.add.text_input('Name: ', default=self.player_data.username, float=True).translate(20, 100)
        self.start_button = self.menu.add.button('Start Game', self.start_game, float=True).translate(20, 100 + button_spacing)
        self.menu.add.button('Random Deck', lambda: self.set_rand_deck(player_data), float=True).translate(20, 100 + button_spacing * 2)
        self.host_button = self.menu.add.button('Host Game', lambda: self.custom_game(True), float=True).translate(20, 100 + button_spacing * 3)
        self.join_button = self.menu.add.button('Join Game', lambda: self.custom_game(False), float=True).translate(20, 100 + button_spacing * 4)
        self.menu.add.button('<- Return', go_to_prev_menu, float=True).translate(20, menu_hight - 60)
        self.in_custom_game = False
        #red highlight for start_button
        red_selection = RedHighlight()
        self.start_button.set_selection_effect(red_selection)

    def custom_game(self, host):
        print(f"inizializing custom game, host: {host}")
        from .st_custom_game import StrategoCustomsWindow
        if self.deck_full():
            green_selection = GreenHighlight()
            if host:
                self.host_button.set_selection_effect(green_selection)
            else:

                self.join_button.set_selection_effect(green_selection)
            self.st_custom_game_menu = StrategoCustomsWindow(
                self.surface,
                go_to_prev_menu=self.go_to_prev_menu,
                go_to_start=self.go_to_start,
                player_data=self.player_data,
                host=host,
                deck=self.deck,
                deck_selector_data=self
            )
            self.in_custom_game = True
        else:
            red_selection = RedHighlight()
            if host:
                self.host_button.set_selection_effect(red_selection)
            else:

                self.join_button.set_selection_effect(red_selection)

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
            print("Caling start_local_server...")
            self.set_deck(self.player_data)
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

    def set_deck(self, global_data: GlobalClientState):
        """
        This method sets the deck.
        """
        flattened_deck = stratego_types.flatten_2d_array(self.deck)
        global_data.stratego_starting_deck_repr = stratego_types.deck_to_socket_message_repr(flattened_deck)


    def empty_pieces(self):
        """
        This method empties the array of pieces from were the player selects his deck
        """
        for row in range(len(self.pieces)):
            for col in range(len(self.pieces[row])):
                self.pieces[row][col] = ''

    def update(self, events: list[Event]):
        """
        Updates the UI.
        """
        #self.in_custom_game = False
        if  self.in_custom_game:
            self.st_custom_game_menu.update(events)

        else:
            self.label.set_value(self.player_data.username)
            if self.deck_full():
                green_selection = GreenHighlight()
                self.start_button.set_selection_effect(green_selection)
            else:
                red_selection = RedHighlight()
                self.start_button.set_selection_effect(red_selection)

            self.menu.update(events)
            self.menu.draw(self.surface)
            for event in events:
                DeckSelector.handle_mouse_event(self, event=event, top_grid=self.deck, bottom_grid=self.pieces)
            DeckSelector.draw(self, surface=self.surface, top_grid=self.deck, bottom_grid=self.pieces)
            pygame.display.flip()



# if __name__ == "__main__":
#    main()