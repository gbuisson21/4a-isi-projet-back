from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

class HashService:
    def __init__(self) -> None:
        self.ph = PasswordHasher()
    
    def hash(self, password):
        return self.ph.hash(password)


    def check_hash(self, password: str, password_hash : str):
        try:
            self.ph.verify(password_hash, password)
            return True
            
        except VerifyMismatchError:
            return False
