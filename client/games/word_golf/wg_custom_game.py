# pyright: reportAttributeAccessIssue=false
# ================================================================+
# Started on:  December 5, 2025                                   |
# Finished on: December 9, 2025                                   |
# Programmed by: Eduardo J. Matos                                 |
# Collaborators:                                                  |
#       * Eduardo J Matos Pérez                                   |
#       * Guillermo Myers                                         |
# ----------------------------------------------------------------+
# Description:                                                    |
#      This code is responsible for managing the custom games     |
#      for Word Golf.                                             |
# ----------------------------------------------------------------+
# Last modification [December 9, 2025]:                           |
#    * The following methods were added:                          |
#                                                                 |
#    * The following methods were eliminated:                     |
#               - layout_menu_widgets                             |
#               - go_back                                         |
#                                                                 |
#    * Other: Resize of the window was fixed and instructions for |
#             join/host mechanics were added.                     |
#                                                                 |
# ================================================================+

# ==========================Imports================================#
import subprocess
from pygame_menu import themes
from ui.drawing_utils import draw_text
from typing import Callable
import pygame
from pygame import Surface
from pygame.event import Event
import pygame_menu
import pyperclip
from common_types.global_state import GlobalClientState
from common_types.game_types import SCREEN_WIDTH, SCREEN_HEIGHT

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
                 ):

        self.surface = surface
        self.player_data = player_data
        # Methods
        self.go_to_start = go_to_start
        self.go_to_prev_menu = go_to_prev_menu
        self.host = host
        # =========================================================#
        self.scale_modification = self.player_data.ui_scale  # Scale modification
        self.prev_scale = self.scale_modification
        # =========================================================#
        self.old_host = self.host
        self.join_msg = [
            "To be able to join a game you must write the host's",
            "code in the code box and wait for the host to start",
            "the server before joining."
        ]
        self.host_msg = [
            "To be able to host a game you must give the code",
            "to the other player before starting the server.",
            "The other player can only join when server starts."
        ]
        # =========================================================#
        self.menu = pygame_menu.Menu('Word Golf', SCREEN_WIDTH, SCREEN_HEIGHT, theme=themes.THEME_SOLARIZED)
        self.join_label = self.menu.add.label(f"{self.join_msg[0]}\n{self.join_msg[1]}\n{self.join_msg[2]}")
        self.host_label = self.menu.add.label(f"{self.host_msg[0]}\n{self.host_msg[1]}\n{self.host_msg[2]}")
        self.code = self.menu.add.label(f"Code: {self.get_public_ip()}")
        self.code_join = self.menu.add.text_input('Code: ', default="", onchange=self.set_ip)
        self.copy_button = self.menu.add.button('Copy code', self.copy_code)
        self.start_game_button = self.menu.add.button('Start Game', self.start_game)
        self.back = self.menu.add.button("<- Back", self.go_to_prev_menu)
        self.first_run = True
        # =========================================================#
        for label in self.join_label:
            label.hide()
        self.code_join.hide()
        for label in self.host_label:
            label.hide()
        self.code.hide()
        self.copy_button.hide()

        if self.host:
            for label in self.host_label:
                label.show()
            self.code.show()
            self.copy_button.show()
        else:
            for label in self.join_label:
                label.show()
            self.code_join.show()

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
            print("Calling start_local_server...")
            self.start_local_server()
        self.go_to_start()

    def update(self, events: list[Event], host):
        """
        Updates the UI.
        """
        self.scale_modification = self.player_data.ui_scale

        if self.prev_scale != self.scale_modification: # If window scale was changed
            # compute new menu size (clamped)
            new_w = max(200, int(SCREEN_WIDTH * self.scale_modification))
            new_h = max(200, int(SCREEN_HEIGHT * self.scale_modification))

            # resize menu
            self.menu.resize(new_w, new_h)

            self.prev_scale = self.scale_modification

        if self.old_host != host: # if the value in host changed (user changed from host to join or join to host)
            self.first_run = True
            self.old_host = host

        if self.first_run: # If in first run

            if host: # Displays Host menu
                print("Setting up code")
                self.code_join.hide()
                for label in self.join_label:
                    label.hide()
                for label in self.host_label:
                    label.show()
                self.code.show()
                self.copy_button.show()

            else: # Displays Join Menu
                self.code.hide()
                for label in self.host_label:
                    label.hide()
                for label in self.join_label:
                    label.show()
                self.code_join.show()
                self.copy_button.hide()

            self.first_run = False

        self.menu.resize(SCREEN_WIDTH*self.scale_modification, SCREEN_HEIGHT*self.scale_modification)
        self.menu.update(events)

        self.menu.draw(self.surface)

        pygame.display.flip()
