import pygame
from pygame.event import Event
from pygame import Surface
from global_state import WordGolfGlobalState


def gen_guess_cmd(guess: str) -> str:
    return f"!guess:{guess}"


def word_golf_update(events: list[Event], surface: Surface, global_game_data: WordGolfGlobalState) -> str | None:
    debug_game_info_caption = f"{global_game_data.own_username} ({global_game_data.own_queued_word_amt}) VS {global_game_data.opp_username} ({global_game_data.opp_queued_word_amt})"

    # Set screen caption.
    pygame.display.set_caption(f"Word Golf - {debug_game_info_caption}")

    # Clear the screen.
    surface.fill((100, 100, 100))

    guess_cmd: str | None = None

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE and len(global_game_data.typed_letters) > 0:
                global_game_data.typed_letters.pop()

            elif event.key == pygame.K_RETURN and len(global_game_data.typed_letters) == 5:
                guess = ''.join(global_game_data.typed_letters)
                guess_cmd = gen_guess_cmd(guess)

            else:
                if 'a' <= event.unicode <= 'z' and len(global_game_data.typed_letters) < 5:
                    global_game_data.typed_letters.append(event.unicode)

    return guess_cmd
            
