import hashlib
import hmac

class SecretGameBackgroundActivator:
    def __init__(self, secret_key_hash: str):
        if len(secret_key_hash) < 64:
            raise ValueError("secret key is not secure enough")
        
        self.secret_key_hash = secret_key_hash
        
        self.user_keypress_acc = ""


    def read_user_key_press(self, key_press: str):
        if key_press < 'a' or key_press > 'z':
            return
        
        self.user_keypress_acc += key_press

        if not self.check_hash():
            return
        
        # TODO: start the secret game
        print("gained access to the system")


    def check_hash(self) -> bool:
        hash_object = hashlib.sha256(self.user_keypress_acc.encode())
        digest = hash_object.hexdigest()

        return hmac.compare_digest(digest, self.secret_key_hash)

        