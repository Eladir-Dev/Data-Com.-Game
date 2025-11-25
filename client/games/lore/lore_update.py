import pygame
from pygame.event import Event
from pygame import Surface

from common_types.global_state import LoreGlobalState

def lore_update(events: list[Event], surface: Surface, global_game_data: LoreGlobalState) -> str | None:
    surface.fill((0, 0, 0))

    if global_game_data.kind == 'secret_game':
        subtitle = "Garage"

    elif global_game_data.kind == 'secret_dlc_store':
        subtitle = "Store"

    elif global_game_data.kind == 'secret_paint_game':
        subtitle = "Paint Shop"

    else:
        subtitle = "Unknown" # unreachable

    pygame.display.set_caption(f"Lore - {subtitle}")

    # TODO: actually add the lore
