import functools
import pygame
from pygame import Surface
from common_types.game_types import Pair

@functools.lru_cache(maxsize=None)
def get_sprite(sprite_file_path: str, target_dimensions: Pair) -> Surface:
    sprite = pygame.image.load(f"{sprite_file_path}")
    sprite_scaled = pygame.transform.scale(sprite, target_dimensions)

    return sprite_scaled.convert_alpha()
