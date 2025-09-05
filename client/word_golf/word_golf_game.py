import pygame
from pygame.event import Event
from pygame import Surface

from game_types import SCREEN_WIDTH
from .word_golf_types import WORD_LEN
from global_state import WordGolfGlobalState
import drawing_utils

def gen_guess_cmd(guess: str) -> str:
    return f"!guess:{guess}"


def draw_feedback_and_typed_word_ui(surface: Surface, global_game_data: WordGolfGlobalState):

    WORD_GOLF_UI_START_POS = (SCREEN_WIDTH // 2, 100)

    # Pad out the typed letters with spaces.
    typed_letters_padded = list(global_game_data.typed_letters)
    if len(typed_letters_padded) < WORD_LEN:
        remaining_len = WORD_LEN - len(typed_letters_padded)
        typed_letters_padded += [' '] * remaining_len

    # Copy the feedback history and append the (padded) typed letters at the end.
    drawing_symbols_grid = list(global_game_data.feedback_history)
    drawing_symbols_grid.append("".join(typed_letters_padded))

    for r in range(len(drawing_symbols_grid)):
        for c in range(WORD_LEN):
            # Transform the row/col coords into Pygame's x/y coords.
            x, y = c, r
            
            symbol = drawing_symbols_grid[r][c]

            SYMBOL_SIZE = 30

            drawing_utils.draw_text(
                surface, 
                symbol, 
                SYMBOL_SIZE, 
                (WORD_GOLF_UI_START_POS[0] + SYMBOL_SIZE * x, WORD_GOLF_UI_START_POS[1] + SYMBOL_SIZE * y),
                (255, 255, 255),
            )
    

def word_golf_update(events: list[Event], surface: Surface, global_game_data: WordGolfGlobalState) -> str | None:
    debug_game_info_caption = f"{global_game_data.own_username} ({global_game_data.own_queued_word_amt} words queued) ({global_game_data.own_points} pts) VS {global_game_data.opp_username} ({global_game_data.opp_queued_word_amt} words queued) ({global_game_data.opp_points} pts)"

    # Set screen caption.
    pygame.display.set_caption(f"Word Golf - {debug_game_info_caption}")

    # Clear the screen.
    surface.fill((100, 100, 100))

    draw_feedback_and_typed_word_ui(surface, global_game_data)

    guess_cmd: str | None = None

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE and len(global_game_data.typed_letters) > 0:
                global_game_data.typed_letters.pop()

            elif event.key == pygame.K_RETURN and len(global_game_data.typed_letters) == WORD_LEN:
                guess = ''.join(global_game_data.typed_letters)
                guess_cmd = gen_guess_cmd(guess)

            else:
                if 'a' <= event.unicode <= 'z' and len(global_game_data.typed_letters) < WORD_LEN:
                    global_game_data.typed_letters.append(event.unicode)

    return guess_cmd
            
