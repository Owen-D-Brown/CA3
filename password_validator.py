from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

password_hasher = PasswordHasher(time_cost=2, memory_cost=19 * 1024, parallelism=1)

def hash_password(password: str) -> str:
    return password_hasher.hash(password)

def verify_password(attempt_password: str, actual_password: str) -> bool:
    try:
        password_hasher.verify(attempt_password, actual_password)
        return True
    except VerifyMismatchError:
        return False