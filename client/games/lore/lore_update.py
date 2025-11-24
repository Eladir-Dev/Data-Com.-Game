import pygame
from pygame.event import Event
from pygame import Surface

from common_types.global_state import LoreGlobalState

def lore_update(events: list[Event], surface: Surface, global_game_data: LoreGlobalState) -> str | None:
    surface.fill((0, 0, 0))
    pygame.display.set_caption("Lore")

    # TODO: actually add the lore
