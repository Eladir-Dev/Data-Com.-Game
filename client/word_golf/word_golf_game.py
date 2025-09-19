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

    WORD_GOLF_MAIN_UI_START_POS = (SCREEN_WIDTH // 2, 100)
    SYMBOL_SIZE = 30

    feedback_amt = len(global_game_data.feedback_history)

    for i in range(feedback_amt):
        feedback = global_game_data.feedback_history[i]

        for j in range(0, len(feedback), 2):
            x, y = j, i

            kind, letter = feedback[j], feedback[j + 1]

            if kind == 'O':
                # Green.
                color = (0, 255, 0)
            elif kind == '!':
                # Yellow.
                color = (255, 255, 0)
            elif kind == 'X':
                # Red.
                color = (255, 0, 0)
            else:
                # Purple (unreachable).
                color = (255, 0, 255)

            drawing_utils.draw_text(
                surface,
                letter,
                SYMBOL_SIZE,
                (WORD_GOLF_MAIN_UI_START_POS[0] + x * SYMBOL_SIZE, WORD_GOLF_MAIN_UI_START_POS[1] + y * SYMBOL_SIZE),
                color,
            )

    # Draw the typed letters.
    for i in range(len(global_game_data.typed_letters)):
        x = i
        drawing_utils.draw_text(
            surface, 
            global_game_data.typed_letters[i].upper(), 
            SYMBOL_SIZE, 
            (WORD_GOLF_MAIN_UI_START_POS[0] + x * SYMBOL_SIZE, WORD_GOLF_MAIN_UI_START_POS[1] + feedback_amt * SYMBOL_SIZE), 
            color=(0, 0, 0),
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
            
