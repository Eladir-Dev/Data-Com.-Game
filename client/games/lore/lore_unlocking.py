import random
from common_types.game_types import GameKind
from games.lore.lore_types import LoreKind

# TODO: These are currently set to 100% for testing purposes; they should be set to a lower percent in practice.
_SECRET_GAME_CUTSCENE_UNLOCK_CHANCE = 1.0
_SECRET_DLC_STORE_CUTSCENE_UNLOCK_CHANCE = 1.0

def _try_unlock_secret_game_lore() -> LoreKind | None:
    if random.random() < _SECRET_GAME_CUTSCENE_UNLOCK_CHANCE:
        return 'secret_game'
    
    return None


def _try_unlock_secret_dlc_store_lore() -> LoreKind | None:
    if random.random() < _SECRET_DLC_STORE_CUTSCENE_UNLOCK_CHANCE:
        return 'secret_dlc_store'
    
    return None


def determine_lore_kind_after_game(game: GameKind) -> LoreKind | None:
    if game in {'stratego', 'word_golf'}:
        return _try_unlock_secret_game_lore()

    elif game == 'secret_game':
        return _try_unlock_secret_dlc_store_lore()
    
    else:
        return None
