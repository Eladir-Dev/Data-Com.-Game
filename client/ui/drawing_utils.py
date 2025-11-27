import pygame
from pygame import Surface, Rect
from common_types.game_types import Pair
from typing import Literal

RectOrigin = Literal['center', 'top_left']


def apply_ui_scale_int(value: int, ui_scale: float) -> int:
    return int(value * ui_scale)


def apply_ui_scale_pair(pair: Pair, ui_scale: float) -> Pair:
    return (int(pair[0] * ui_scale), int(pair[1] * ui_scale))


def draw_sprite_on_surface(surface: Surface, ui_scale: float, sprite: Surface, location: Pair, target_dimensions: Pair, rotation_deg: float = 0.0, rect_origin: RectOrigin = 'center') -> Rect:
    location = apply_ui_scale_pair(location, ui_scale)
    target_dimensions = apply_ui_scale_pair(target_dimensions, ui_scale)

    # TODO: remove this and do the scaling separately. scaling each frame is laggy.
    # sprite = pygame.transform.scale(sprite, target_dimensions)
    
    if rotation_deg != 0.0:
        sprite = pygame.transform.rotate(sprite, rotation_deg)

    if rect_origin == 'top_left':
        sprite_rect = sprite.get_rect(topleft=location)
    else: # center (default)
        sprite_rect = sprite.get_rect(center=location)

    surface.blit(sprite, sprite_rect)
    return sprite_rect


def draw_text(surface: Surface, ui_scale: float, text: str, font_size: int, location: Pair, color: tuple[int, int, int]) -> Rect:
    font_size = apply_ui_scale_int(font_size, ui_scale)
    location = apply_ui_scale_pair(location, ui_scale)

    font = pygame.font.SysFont(None, font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=location)
    surface.blit(text_surface, text_rect)
    return text_rect


def draw_colored_rect(surface: Surface, ui_scale: float, location: Pair, width: int, height: int, color: tuple[int, int, int]) -> Rect:
    location = apply_ui_scale_pair(location, ui_scale)
    width, height = apply_ui_scale_pair((width, height), ui_scale)

    rect_data = (location[0] - width // 2, location[1] - height // 2, width, height)
    return pygame.draw.rect(
        surface,
        color,
        rect_data,
    )