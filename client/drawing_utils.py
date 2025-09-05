import pygame
from pygame import Surface, Rect
from game_types import Pair

def draw_sprite_on_surface(surface: Surface, sprite: Surface, location: Pair, target_dimensions: Pair) -> Rect:
    scaled = pygame.transform.scale(sprite, target_dimensions)
    sprite_rect = scaled.get_rect(center=location)
    surface.blit(scaled, sprite_rect)
    return sprite_rect


def draw_text(surface: Surface, text: str, font_size: int, location: Pair, color: tuple[int, int, int]):
    font = pygame.font.SysFont(None, font_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=location)
    surface.blit(text_surface, text_rect)