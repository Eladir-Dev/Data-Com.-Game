import hashlib
import hmac
from typing import Callable

class SecretGameBackgroundActivator:
    def __init__(
        self,
        secret_key_hash: str,
        start_loading_secret_game: Callable[[], None],
    ):
        if len(secret_key_hash) < 64:
            raise ValueError("secret key is not secure enough")
        
        self.secret_key_hash = secret_key_hash
        self.start_loading_secret_game = start_loading_secret_game
        
        self.user_keypress_acc = ""


    def read_user_key_press(self, key_press: str):
        if key_press < 'a' or key_press > 'z':
            return
        
        self.user_keypress_acc += key_press

        if not self.check_hash():
            return
        
        self.start_loading_secret_game()


    def check_hash(self) -> bool:
        hash_object = hashlib.sha256(self.user_keypress_acc.encode())
        digest = hash_object.hexdigest()

        return hmac.compare_digest(digest, self.secret_key_hash)

        