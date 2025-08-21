import socket
from socket import socket as Connection
import threading
import time
from typing import Literal

# Types.
StrategoColor = Literal['r', 'b']

# Constants.
ROWS = 10
COLS = 10
DECK_ROWS = 4