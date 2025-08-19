# """
# Currently this module implements a UI for a simple chat between two clients.
# TODO: Actually implement the game.
# """

# import pygame
# import sys
# import client_core
# import threading
# import queue

# # Screen dimensions
# SCREEN_WIDTH = 800
# SCREEN_HEIGHT = 600

# # Colors
# WHITE = (255, 255, 255)
# BLACK = (0, 0, 0)
# GRAY = (100, 100, 100)
# LIGHT_GRAY = (200, 200, 200)

# SOCKET_SERVER_CMD_QUEUE: queue.Queue[str] = queue.Queue()
# SOCKET_CLIENT_QUEUE: queue.Queue[str] = queue.Queue()

# SOCKET_CLIENT_THREAD = threading.Thread(target=client_core.connect, args=(SOCKET_SERVER_CMD_QUEUE, SOCKET_CLIENT_QUEUE))
# SOCKET_CLIENT_THREAD.daemon = True # Allows the program to exit even if the thread is running.
# SOCKET_CLIENT_THREAD.start()

# PLAYER_ROLE = "UNKNOWN"

# def run_event_loop():
#     # Initialize Pygame.
#     pygame.init()

#     # Create the screen.
#     screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
#     pygame.display.set_caption("Pygame Client")

#     # Font for text rendering.
#     font = pygame.font.Font(None, 32)

#     # Input box variables.
#     input_box_rect = pygame.Rect(50, 500, 700, 40)
#     active_color = LIGHT_GRAY
#     inactive_color = GRAY
#     input_box_color = inactive_color
#     text_input = ""
#     text_output = ""

#     # Main game loop.
#     running = True

#     while running:
#         while not SOCKET_SERVER_CMD_QUEUE.empty():
#             server_cmd = SOCKET_SERVER_CMD_QUEUE.get()
#             print(f"LOG: SOCKET COMMAND: {server_cmd}")

#             if server_cmd.startswith("?game-start"):
#                 own_role_number = int(server_cmd.split(" ")[1])
#                 opp_role_number = 1 if own_role_number == 2 else 2
#                 OPPONENT_ROLE = f"Player {opp_role_number}"
#             elif server_cmd == "?game-over":
#                 running = False
#             elif server_cmd.startswith("?message"):
#                 content = " ".join(server_cmd.split(" ")[1:])
#                 text_output = f"{OPPONENT_ROLE}: {content}"

#         # Event handling
#         for event in pygame.event.get():

#             if event.type == pygame.QUIT:
#                 running = False

#             if event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_RETURN:
#                     # Process the input here.
#                     # For testing, we'll just move the input to the output.
#                     # text_output = "You said: " + text_input
#                     SOCKET_CLIENT_QUEUE.put(text_input)
#                     text_input = "" # Clear the input box.

#                 elif event.key == pygame.K_BACKSPACE:
#                     text_input = text_input[:-1]
#                 else:
#                     text_input += event.unicode

#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 # Check if the user clicked on the input box
#                 if input_box_rect.collidepoint(event.pos):
#                     input_box_color = active_color

#                 else:
#                     input_box_color = inactive_color

#         # Drawing to the screen
#         screen.fill(BLACK)

#         # Draw the output text
#         output_surface = font.render(text_output, True, WHITE)
#         screen.blit(output_surface, (50, 450))

#         # Draw the input box
#         pygame.draw.rect(screen, input_box_color, input_box_rect, 2)
#         text_surface = font.render(text_input, True, WHITE)
#         screen.blit(text_surface, (input_box_rect.x + 5, input_box_rect.y + 5))

#         # Update the display
#         pygame.display.flip()

#     # Quit Pygame
#     pygame.quit()
#     sys.exit()