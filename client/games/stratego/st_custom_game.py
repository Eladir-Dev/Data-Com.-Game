# pyright: reportAttributeAccessIssue=false
# ================================================================+
# Started on:  November 5, 2025                                   |
# Finished on: _______                                            |
# Programmed by: Eduardo J. Matos                                 |
# Collaborators:                                                  |
#       * Eduardo J Matos Pérez                                   |
#       * Guillermo Myers                                         |
# ----------------------------------------------------------------+
# Description:                                                    |
#      This code is responsible for managing the custom games     |
#      for Stratego. It is a sub-window/menu of deck_selection    |
# ----------------------------------------------------------------+
# Last modification [November 9, 2025]:                           |
#    * The following methods were added:  start_local_server      |
#                                                                 |
#    * The following methods were eliminated:                     |
#                                                                 |
#    * Other: Code was refined and worked on                      |
#                                                                 |
# ================================================================+
import subprocess

#==========================Imports================================#
from ui.drawing_utils import draw_text
from typing import Callable
import pygame
from pygame import Surface
from pygame.event import Event
import pygame_menu
from pygame_menu.widgets.core.selection import Selection
import pyperclip
from .deck_selection import StrategoSettingsWindow
from common_types.global_state import GlobalClientState
from common_types.game_types import SCREEN_WIDTH, SCREEN_HEIGHT
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
    This static class takes care of drawing the grids for the deck selection.
    """

    @staticmethod
    def draw(window: "StrategoCustomsWindow", surface: Surface, bottom_grid):
        """
        This function draws the grids and sprites for the Deck selection screen.
        """
        for key in window.sprites:
            window.sprites[key] = pygame.transform.scale(window.sprites[key], (window.CELL_SIZE, window.CELL_SIZE))

        # Constants
        CELL_SIZE = int(50 * window.scale_modification)
        GRID_COLS = 10
        GRID_ROWS = 4
        TOP_GRID_Y = 70
        BOTTOM_GRID_Y = int(340 * window.scale_modification)
        X_START = int(336 * window.scale_modification)
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


        pygame.draw.rect(surface, BLUE_BAR,
                         (0, 0, 900 * window.scale_modification, 40 * window.scale_modification))  # Upper bar

        pygame.draw.rect(surface, LIGHT_GRAY2, (0, 40 * window.scale_modification, 900 * window.scale_modification,
                                                3 * window.scale_modification))  # lines

        # Render main text
        draw_text(surface, 1, "Stratego", 36,
                  (int(SCREEN_WIDTH * window.scale_modification // 2), int(20 * window.scale_modification)), (255, 255, 255))
        if window.first_run:
            pygame.draw.rect(surface, CREMA,
                             (275 * window.scale_modification, 30 * window.scale_modification, 650 * window.scale_modification,
                              600 * window.scale_modification))  # Background

            pygame.draw.rect(surface, (51, 49, 45),
                             (300 * window.scale_modification, 50 * window.scale_modification, 575 * window.scale_modification,
                              520 * window.scale_modification))  # Grid backgrounds

            join_msg = [
                    "To be able to join a game you must write the host's",
                    "code in the code box and wait for the host to start",
                    "the server before joining."
                    ]
            host_msg = [
                    "To be able to host a game you must give the code",
                    "to the other player before starting the server.",
                    "The other player can only join when server starts."
                    ]
            marg_mod = 50

            draw_x_pos = int(1175 * window.scale_modification // 2)
            
            if window.host:
                # Render host game instructions
                draw_text(surface, 1, host_msg[0], 30,
                          (draw_x_pos, int(marg_mod + 100 * window.scale_modification)), (255, 255, 255))
                draw_text(surface, 1, host_msg[1], 30,
                          (draw_x_pos, int(marg_mod + 125 * window.scale_modification)), (255, 255, 255))
                draw_text(surface, 1, host_msg[2], 30,
                          (draw_x_pos, int(marg_mod + 150 * window.scale_modification)), (255, 255, 255))
            else:
                # Render join game instructions
                draw_text(surface, 1, join_msg[0], 30,
                          (draw_x_pos, int(marg_mod + 100 * window.scale_modification)),
                          (255, 255, 255))
                draw_text(surface, 1, join_msg[1], 30,
                          (draw_x_pos, int(marg_mod + 125 * window.scale_modification)),
                          (255, 255, 255))
                draw_text(surface, 1, join_msg[2], 30,
                          (draw_x_pos, int(marg_mod + 150 * window.scale_modification)),
                          (255, 255, 255))
            window.first_run = False


        # Bottom grid outline: Identical to top for consistency.
        for row in range(GRID_ROWS + 1):
            y = BOTTOM_GRID_Y + row * CELL_SIZE
            pygame.draw.line(surface, WHITE, (X_START, y), (X_START + GRID_COLS * CELL_SIZE, y), 2)
        for col in range(GRID_COLS + 1):
            x = X_START + col * CELL_SIZE
            pygame.draw.line(surface, WHITE, (x, BOTTOM_GRID_Y), (x, BOTTOM_GRID_Y + GRID_ROWS * CELL_SIZE), 2)


        # Draw pieces in the bottom grid based on self.bottom_grid
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                piece = bottom_grid[row][col]
                if piece != "":  # Only draw if there's a piece
                    x = X_START + col * CELL_SIZE
                    y = BOTTOM_GRID_Y + row * CELL_SIZE
                    surface.blit(window.sprites[piece], (x, y))  # Blit the sprite at the cell's top-left

class StrategoCustomsWindow():
    def __init__(self,
        surface: Surface,
        go_to_prev_menu: Callable[[], None],
        go_to_start: Callable[[], None],
        player_data: GlobalClientState,
        host: bool,
        deck: list[list[str]],
        deck_selector_data: StrategoSettingsWindow
    ):

        # pygame.mixer.music.load("games/stratego/sfx/game_music_v1.wav")
        # pygame.mixer.music.set_volume(.25)
        # pygame.mixer.music.play(-1, 0.0)

        self.surface = surface
        # Methods
        self.go_to_start = go_to_start
        self.go_to_prev_menu = go_to_prev_menu
        self.host = host
        self.deck_selector_data = deck_selector_data

        self.first_run = True
        #======================Custom theme======================#
        self.theme = pygame_menu.themes.THEME_DARK.copy()
        self.theme.widget_alignment = pygame_menu.locals.ALIGN_LEFT
        self.theme.title = False  # Optional: hide title
        self.theme.widget_font_size = 25
        # ======================Deck data=========================#
        rows = 10
        cols = 4
        self.player_data = player_data
        #self.pieces = [['' for _ in range(rows)] for _ in range(cols)]
        self.deck = deck
        #self.fill_pieces(rows, cols, True)
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
        self.original_sprites = {
            "S": pygame.image.load(f"{SPRITE_FOLDER}/red_spy.png").convert_alpha(),
            "1": pygame.image.load(f"{SPRITE_FOLDER}/red_marshal.png").convert_alpha(),
            "G": pygame.image.load(f"{SPRITE_FOLDER}/red_general.png").convert_alpha(),
            "2": pygame.image.load(f"{SPRITE_FOLDER}/red_coronel.png").convert_alpha(),
            "3": pygame.image.load(f"{SPRITE_FOLDER}/red_major.png").convert_alpha(),
            "C": pygame.image.load(f"{SPRITE_FOLDER}/red_captain.png").convert_alpha(),
            "L": pygame.image.load(f"{SPRITE_FOLDER}/red_lieutenant.png").convert_alpha(),
            "4": pygame.image.load(f"{SPRITE_FOLDER}/red_sergeant.png").convert_alpha(),
            "8": pygame.image.load(f"{SPRITE_FOLDER}/red_scout.png").convert_alpha(),
            "5": pygame.image.load(f"{SPRITE_FOLDER}/red_miner.png").convert_alpha(),
            "B": pygame.image.load(f"{SPRITE_FOLDER}/red_bomb.png").convert_alpha(),
            "F": pygame.image.load(f"{SPRITE_FOLDER}/red_flag.png").convert_alpha(),
        }
        # =========================================================#
        self.scale_modification = self.player_data.ui_scale  # Scale modification
        self.prev_scale = self.scale_modification
        # =========================================================#

        # Create menu with left-side layout
        self.menu_height = 600
        self.menu_width = 275
        self.menu = pygame_menu.Menu(
            height=self.menu_height,
            width=self.menu_width,  # Sidebar width
            title='Game Options',
            theme=self.theme,
            center_content=False  # Disable auto-centering
        )
        self.menu.set_relative_position(0, 10)
        # Add widgets with manual positioning
        self.menu_title = self.menu.add.label('==Custom Game==', float=True).translate(5, 35)
        button_spacing = 60
        self.label = self.menu.add.text_input('Name: ', default=self.player_data.username, float=True).translate(20, 100)
        self.start_button = self.menu.add.button('Start Game', self.start_game, float=True).translate(20, 100 + button_spacing)

        if host:
            self.ip=self.menu.add.label(f"Code: {self.get_public_ip()}", float=True).translate(20, SCREEN_HEIGHT // 2)
            #draw_text(surface, f"{self.get_public_ip()}", 36, (SCREEN_WIDTH // 2, 100), (255, 255, 255))
            self.copy_button = self.menu.add.button('Copy code',
                                                   self.copy_code, float=True).translate(20,
                                                            (SCREEN_HEIGHT // 2) + button_spacing)
        else:
            self.ip = self.menu.add.text_input('Code: ', default="", onchange=self.set_ip ).translate(20,SCREEN_HEIGHT // 2)


        self.return_b = self.menu.add.button('<- Return', self.go_back, float=True).translate(20, self.menu_height - 60)

        #red highlight for start_button
        red_selection = RedHighlight()
        self.start_button.set_selection_effect(red_selection)

        new_w = max(200, int(self.menu_width * self.scale_modification))
        new_h = max(200, int(self.menu_height * self.scale_modification))

        # resize menu
        self.menu.resize(new_w, new_h)
        self.menu.set_relative_position(0, int(10 * self.scale_modification))

        # recompute widget positions for the new size
        self.layout_menu_widgets()

        self.rescale_sprites()
        self.prev_scale = self.scale_modification

    def copy_code(self):
        """
        This method save the IP address to the clipboard.
        """
        pyperclip.copy(self.get_public_ip())

    def set_ip(self, ip):
        """
        Sets the ip of the host
        """
        self.ip = ip

    def get_public_ip(self):
        """
        Returns the local IP address of the machine.
        """
        import socket
        try:
            # Create a socket and connect to an external server to get the local IP.
            # This doesn't actually send data, it just establishes a route.
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]

            return local_ip

        except Exception as e:
            print(f"ERROR: Could not get local IP: {e}")
            return "127.0.0.1"


    def go_back(self):
        """
        Retruns to the previous menu
        """
        self.deck_selector_data.in_custom_game = False


    def start_local_server(self):
        """
        Start the local server
        """
        command = ["python", "../server/main.py", "host"]
        print("Trying to start server...")

        try:
            print("Starting local server in the background...")
            # Popen starts the process without waiting
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Optional: Check if it started successfully after a short delay
            import time
            time.sleep(1)  # Wait 1 second
            if process.poll() is None:  # poll() returns None if still running
                print("Server appears to be running.")
            else:
                stdout, stderr = process.communicate()
                print(f"Server failed to start. Return code: {process.returncode}")
                print("Stdout:", stdout.decode())
                print("Stderr:", stderr.decode())

        except FileNotFoundError:
            print("Error: Python interpreter or script not found.")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def start_game(self):
        """
        This method starts the game.
        """

        print("Starting game...")
        if self.host:
            print("Caling start_local_server...")
            self.start_local_server()
        self.go_to_start()

    def layout_menu_widgets(self):
        """
        This method lays out the menu widget.
        """
        # After any resize, recompute widget positions
        w, h = self.menu.get_size()  # current menu size
        pad = int(20 * self.scale_modification)
        top = int(100 * self.scale_modification)
        spacing = int(60 * self.scale_modification)

        # left padding stays within menu
        self.menu_title.translate(pad, int(37 * self.scale_modification))
        self.label.translate(pad, top)
        self.start_button.translate(pad, top + spacing)
        self.ip.translate(pad, h//2)
        if self.host:
            self.copy_button.translate(pad, (h//2) + spacing)
        self.return_b.translate(pad, h - int(60 * self.scale_modification))

    def rescale_sprites(self):
        """
        Rescales the size of the sprites
        """
        target = int(50 * self.scale_modification)

        # Only scale if size changed
        if target != self.CELL_SIZE:
            self.CELL_SIZE = target
            self.sprites = {}

            for key, image in self.original_sprites.items():
                self.sprites[key] = pygame.transform.smoothscale(
                    image, (self.CELL_SIZE, self.CELL_SIZE)
                )

    def update(self, events: list[Event]):
        """
        Updates the UI.
        """
        self.label.set_value(self.player_data.username)

        self.menu.update(events)

        self.menu.draw(self.surface)

        DeckSelector.draw(window=self, surface=self.surface, bottom_grid=self.deck)

        pygame.display.flip()
