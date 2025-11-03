from typing import Literal
from dataclasses import dataclass

@dataclass
class SecretDLCStoreDownloadProgress:
    percentage: float
    kind: Literal['download_progress'] = 'download_progress'


class SecretDLCIntallationFinish:
    kind: Literal['installation_finish'] = 'installation_finish'


class SecretDLCGameFinish:
    kind: Literal['game_finish'] = 'game_finish'


class SecretDLCGError:
    kind: Literal['error'] = 'error'


SecretDLCStoreUpdate = SecretDLCStoreDownloadProgress | SecretDLCIntallationFinish | SecretDLCGameFinish | SecretDLCGError

