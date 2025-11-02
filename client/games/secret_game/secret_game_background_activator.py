import hashlib
import hmac
from typing import Callable
from common_types.global_state import GlobalClientState

class SecretGameBackgroundActivator:
    def __init__(
        self,
        secret_key_hash: str,
        client_state: GlobalClientState,
        start_loading_secret_game: Callable[[], None],
    ):
        if len(secret_key_hash) < 64:
            raise ValueError("secret key is not secure enough")
        
        self.secret_key_hash = secret_key_hash
        self.client_state = client_state
        self.start_loading_secret_game = start_loading_secret_game
        
        self.user_keypress_acc = ""


    def read_user_key_press(self, key_press: str):
        if key_press < 'a' or key_press > 'z':
            return
        
        # Reset the accumulated key presses.
        if key_press == 'x':
            self.user_keypress_acc = ""
            return
        
        self.user_keypress_acc += key_press

        if not self.check_hash():
            return

        # Fix the username (may contain the secret code).
        idx = self.client_state.username.find('x')
        self.client_state.username = self.client_state.username[:idx]

        self.start_loading_secret_game()


    def check_hash(self) -> bool:
        hash_object = hashlib.sha256(self.user_keypress_acc.encode())
        digest = hash_object.hexdigest()

        return hmac.compare_digest(digest, self.secret_key_hash)

        