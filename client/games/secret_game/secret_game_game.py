from pygame.event import Event
from pygame import Surface
from common_types.global_state import SecretGameGlobalState
import pygame

def secret_game_update(events: list[Event], surface: Surface, global_game_data: SecretGameGlobalState):
    # TODO
    surface.fill((0, 0, 0))

    debug_string = f"{global_game_data.own_username} VS {global_game_data.opp_username}"
    pygame.display.set_caption(debug_string)