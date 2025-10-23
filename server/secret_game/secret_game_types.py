from dataclasses import dataclass
from server_types import Connection

@dataclass
class SecretGamePlayer:
    conn: Connection
    username: str