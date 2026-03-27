import base64
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionManager:
    ITERATIONS = 390000

    @staticmethod
    def generate_salt() -> bytes:
        return os.urandom(16)

    @classmethod
    def derive_key(cls, master_password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=cls.ITERATIONS,
        )
        return base64.urlsafe_b64encode(kdf.derive(master_password.encode("utf-8")))

    @classmethod
    def encrypt_password(cls, plaintext: str, master_password: str, salt: bytes) -> bytes:
        return Fernet(cls.derive_key(master_password, salt)).encrypt(plaintext.encode("utf-8"))

    @classmethod
    def decrypt_password(cls, encrypted_password: bytes, master_password: str, salt: bytes) -> str:
        try:
            decrypted = Fernet(cls.derive_key(master_password, salt)).decrypt(encrypted_password)
        except InvalidToken as exc:
            raise ValueError("Master password verification failed.") from exc
        return decrypted.decode("utf-8")
