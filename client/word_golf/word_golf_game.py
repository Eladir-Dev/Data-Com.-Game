import pygame
from pygame.event import Event
from pygame import Surface

from game_types import SCREEN_WIDTH, SCREEN_HEIGHT
from .word_golf_types import WORD_LEN, MAX_FEEDBACK_HIST_SIZE, Color, RenderedStashedWord, WordGolfUpdateResult
from global_state import WordGolfGlobalState
import drawing_utils

SYMBOL_SIZE = 60
MAIN_UI_WIDTH = SYMBOL_SIZE * WORD_LEN
WORD_GOLF_MAIN_UI_START_POS = ((SCREEN_WIDTH - MAIN_UI_WIDTH) // 2, 40)

def gen_guess_cmd(guess: str) -> str:
    return f"!guess:{guess}"


def gen_stashed_word_cmd(stashed_word: str) -> str:
    return f"!send-stashed-word:{stashed_word}"


def draw_all_ui(surface: Surface, global_game_data: WordGolfGlobalState) -> list[RenderedStashedWord]:
    draw_feedback_and_typed_word_ui(surface, global_game_data)
    draw_points_and_queued_word_ui(surface, global_game_data)
    rendered_stashed_words = draw_stashed_word_ui(surface, global_game_data)

    return rendered_stashed_words


def draw_feedback_and_typed_word_ui(surface: Surface, global_game_data: WordGolfGlobalState):
    feedback_amt = len(global_game_data.feedback_history)

    for i in range(feedback_amt):
        feedback = global_game_data.feedback_history[i]

        for j in range(0, len(feedback), 2):
            x, y = j // 2, i

            kind, letter = feedback[j], feedback[j + 1]

            if kind == 'O':
                color = Color.GREEN
            elif kind == '!':
                color = Color.YELLOW
            elif kind == 'X':
                color = Color.RED
            else:
                color = Color.MAGENTA

            draw_location = (WORD_GOLF_MAIN_UI_START_POS[0] + x * SYMBOL_SIZE, WORD_GOLF_MAIN_UI_START_POS[1] + y * SYMBOL_SIZE)

            rect_size = SYMBOL_SIZE * 8 // 9

            # left, top, width, height
            rect_data = (draw_location[0] - rect_size // 2, draw_location[1] - rect_size // 2, rect_size, rect_size)
            pygame.draw.rect(
                surface,
                color,
                rect_data,
            )

            drawing_utils.draw_text(
                surface,
                letter,
                SYMBOL_SIZE,
                draw_location,
                color=Color.BLACK,
            )

    # Draw the typed letters.
    for i in range(len(global_game_data.typed_letters)):
        x = i
        drawing_utils.draw_text(
            surface, 
            global_game_data.typed_letters[i].upper(), 
            SYMBOL_SIZE, 
            (WORD_GOLF_MAIN_UI_START_POS[0] + x * SYMBOL_SIZE, WORD_GOLF_MAIN_UI_START_POS[1] + feedback_amt * SYMBOL_SIZE), 
            color=Color.WHITE,
        )
    

def draw_points_and_queued_word_ui(surface: Surface, global_game_data: WordGolfGlobalState):
    # Draw the points and queued words UI after the main UI.
    points_ui_start_location = (SCREEN_WIDTH // 2, WORD_GOLF_MAIN_UI_START_POS[1] + MAX_FEEDBACK_HIST_SIZE * SYMBOL_SIZE)
    font_size = SYMBOL_SIZE * 3 // 4

    drawing_utils.draw_text(
        surface,
        f"{global_game_data.own_username}: ({global_game_data.own_queued_word_amt} words queued) - ({global_game_data.own_points} pts)",
        font_size,
        points_ui_start_location,
        color=Color.WHITE,
    )

    drawing_utils.draw_text(
        surface,
        f"{global_game_data.opp_username} ({global_game_data.opp_queued_word_amt} words queued) ({global_game_data.opp_points} pts)",
        font_size,
        location=(points_ui_start_location[0], points_ui_start_location[1] + font_size),
        color=Color.WHITE,
    )


def draw_stashed_word_ui(surface: Surface, global_game_data: WordGolfGlobalState) -> list[RenderedStashedWord]:
    # Draw the stashed words UI after the points UI.
    font_size = SYMBOL_SIZE * 3 // 5
    points_ui_start_location = (0, SCREEN_HEIGHT - font_size)

    rendered_stashed_words: list[RenderedStashedWord] = []

    for i in range(len(global_game_data.stashed_words)):
        x = i
        word = global_game_data.stashed_words[i]
        
        word_offset = (x + 1) * font_size * len(word) // 2

        text_rect = drawing_utils.draw_text(
            surface,
            word,
            font_size,
            (points_ui_start_location[0] + word_offset, points_ui_start_location[1]),
            Color.WHITE,
        )
        rendered_stashed_words.append(RenderedStashedWord(
            rect=text_rect,
            word=word,
        ))

    return rendered_stashed_words


def word_golf_update(events: list[Event], surface: Surface, global_game_data: WordGolfGlobalState) -> WordGolfUpdateResult:
    # Set screen caption.
    pygame.display.set_caption(f"Word Golf")

    # Clear the screen.
    surface.fill(Color.BLACK)

    rendered_stashed_words = draw_all_ui(surface, global_game_data)

    guess_cmd: str | None = None
    stashed_word_cmd: str | None = None

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

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            for rendered_stashed_word in rendered_stashed_words:
                word_rect = rendered_stashed_word.rect

                if word_rect.collidepoint(mouse_pos):
                    # print(rendered_stashed_word.word)
                    stashed_word_cmd = gen_stashed_word_cmd(rendered_stashed_word.word)

    return WordGolfUpdateResult(
        guess_cmd=guess_cmd,
        stashed_word_cmd=stashed_word_cmd,
    )
            
