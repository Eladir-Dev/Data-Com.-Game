from pygame.event import Event
from pygame import Surface
from common_types.global_state import SecretGameGlobalState
import pygame
from pathlib import Path
from ui.drawing_utils import draw_sprite_on_surface
from common_types.game_types import SCREEN_HEIGHT

SPITE_FOLDER = Path(__file__).parent / "assets"


def temp_draw_players(surface: Surface, global_game_data: SecretGameGlobalState):
    p1_sprite = pygame.image.load(f"{SPITE_FOLDER}/player_01.png")
    p2_sprite = pygame.image.load(f"{SPITE_FOLDER}/player_02.png")

    # TODO: Figure out how to render the map and render the corresponding player at the center of the screen.

    draw_sprite_on_surface(
        surface,
        p1_sprite,
        location=(global_game_data.players[0].position[0], SCREEN_HEIGHT // 2),
        target_dimensions=(32, 32),
    )

    draw_sprite_on_surface(
        surface,
        p2_sprite,
        location=(global_game_data.players[1].position[0], SCREEN_HEIGHT // 2),
        target_dimensions=(32, 32),
    )


def secret_game_update(events: list[Event], surface: Surface, global_game_data: SecretGameGlobalState):
    # TODO
    surface.fill((0, 0, 0))

    debug_string = f"{global_game_data.get_own_data().username} ({global_game_data.get_own_data().position}) " + \
        f"VS {global_game_data.get_opp_data().username} ({global_game_data.get_opp_data().position})"
    
    temp_draw_players(surface, global_game_data)

    pygame.display.set_caption(debug_string)