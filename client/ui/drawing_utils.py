import pygame
from pygame import Surface, Rect
from common_types.game_types import Pair
from typing import Literal

RectOrigin = Literal['center', 'top_left']

def draw_sprite_on_surface(surface: Surface, sprite: Surface, location: Pair, target_dimensions: Pair, rotation_deg: float = 0.0, rect_origin: RectOrigin = 'center') -> Rect:
    sprite = pygame.transform.rotate(pygame.transform.scale(sprite, target_dimensions), rotation_deg)

    if rect_origin == 'top_left':
        sprite_rect = sprite.get_rect(topleft=location)
    else: # center (default)
        sprite_rect = sprite.get_rect(center=location)

    surface.blit(sprite, sprite_rect)
    return sprite_rect


def draw_text(surface: Surface, text: str, font_size: int, location: Pair, color: tuple[int, int, int]) -> Rect:
    font = pygame.font.SysFont(None, font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=location)
    surface.blit(text_surface, text_rect)
    return text_rect