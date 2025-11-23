import pygame
from pathlib import Path

GAMES_DIR = Path(__file__).parent.parent / "games"

STRATEGO_MUSIC_PATH = GAMES_DIR / "stratego" / "sfx" / "Brirfing_theme.mp3"
WORD_GOLF_MUSIC_PATH = GAMES_DIR / "word_golf" / "sfx" / "b423b42.wav"
SECRET_GAME_MUSIC_PATH = GAMES_DIR / "secret_game" / "assets" / "Bone Yard Waltz - Loopable.ogg"

def play_stratego_bg_music():
    _play_looping_bg_music(STRATEGO_MUSIC_PATH)


def play_word_golf_bg_music():
    _play_looping_bg_music(WORD_GOLF_MUSIC_PATH)


def play_secret_game_bg_music():
    _play_looping_bg_music(SECRET_GAME_MUSIC_PATH)


def _play_looping_bg_music(path: Path):
    pygame.mixer.music.load(path)
    pygame.mixer.music.play(-1)


def stop_all_bg_music():
    pygame.mixer.music.stop()