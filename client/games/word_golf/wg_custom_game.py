# pyright: reportAttributeAccessIssue=false
# ================================================================+
# Started on:  December 5, 2025                                   |
# Finished on: _______                                            |
# Programmed by: Eduardo J. Matos                                 |
# Collaborators:                                                  |
#       * Eduardo J Matos Pérez                                   |
#       * Guillermo Myers                                         |
# ----------------------------------------------------------------+
# Description:                                                    |
#      This code is responsible for managing the custom games     |
#      for Word Golf.                                              |
# ----------------------------------------------------------------+
# Last modification [December 5, 2025]:                           |
#    * The following methods were added: Some from st_custom_game |
#                                                                 |
#    * The following methods were eliminated: several             |
#                                                                 |
#    * Other:                                                     |
#                                                                 |
# ================================================================+
import subprocess

# ==========================Imports================================#
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

# =================================================================#
class WordGolfCustomsWindow():
    """
    This class takes care of Word Golf's custom game screen.
    """
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

        #TODO: To be implemented.

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
        self.ip.translate(pad, h // 2)
        if self.host:
            self.copy_button.translate(pad, (h // 2) + spacing)
        self.return_b.translate(pad, h - int(60 * self.scale_modification))

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
