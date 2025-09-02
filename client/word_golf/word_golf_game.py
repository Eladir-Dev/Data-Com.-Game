import pygame
from pygame.event import Event
from pygame import Surface
from global_state import WordGolfGlobalState

def word_golf_update(events: list[Event], surface: Surface, global_game_data: WordGolfGlobalState):
    debug_game_info_caption = f"{global_game_data.own_username} ({global_game_data.own_queued_word_amt}) VS {global_game_data.opp_username} ({global_game_data.opp_queued_word_amt})"

    # Set screen caption.
    pygame.display.set_caption(f"Word Golf - {debug_game_info_caption}")

    # Clear the screen.
    surface.fill((100, 100, 100))
