from pygame.event import Event
from pygame import Surface
from common_types.global_state import SecretGameGlobalState

def secret_game_update(events: list[Event], surface: Surface, global_game_data: SecretGameGlobalState):
    # TODO
    surface.fill((0, 0, 0))