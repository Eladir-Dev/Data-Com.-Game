import pygame
from pathlib import Path

MAIN_MENU_MUSIC_PATH = Path(__file__).parent / "sfx" / "awesomeness.wav"

GAMES_DIR = Path(__file__).parent.parent / "games"

STRATEGO_MUSIC_PATH = GAMES_DIR / "stratego" / "sfx" / "Brirfing_theme.mp3"
WORD_GOLF_MUSIC_PATH = GAMES_DIR / "word_golf" / "sfx" / "b423b42.wav"
SECRET_GAME_MUSIC_PATH = GAMES_DIR / "secret_game" / "assets" / "Bone Yard Waltz - Loopable.ogg"
LORE_MUSIC_PATH = GAMES_DIR / "lore" / "sfx" / "Snowfall (Looped ver.).ogg"
SECRET_PAINT_GAME_MUSIC_PATH = GAMES_DIR / "secret_paint_game" / "sfx" / "song21.mp3"

def play_main_menu_bg_music():
    _play_looping_bg_music(MAIN_MENU_MUSIC_PATH)


def play_stratego_bg_music():
    _play_looping_bg_music(STRATEGO_MUSIC_PATH)


def play_word_golf_bg_music():
    _play_looping_bg_music(WORD_GOLF_MUSIC_PATH)


def play_secret_game_bg_music():
    _play_looping_bg_music(SECRET_GAME_MUSIC_PATH)


def play_lore_bg_music():
    _play_looping_bg_music(LORE_MUSIC_PATH)


def play_secret_paint_game_bg_music():
    _play_looping_bg_music(SECRET_PAINT_GAME_MUSIC_PATH)


def _play_looping_bg_music(path: Path):
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(-1)


def stop_all_bg_music():
    pygame.mixer.music.stop()