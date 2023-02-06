import json
from io import BytesIO

from cryptography.fernet import Fernet


class Utils:
    def __init__(self, version: str):
        self.version = version

    def create_settings(self) -> None:
        """
        Check if settings.json exists if it does not exist it
        creates it create settings.json file.
        :return:
        """
        try:
            with open('settings.json', 'r') as f:
                f.read()
        except FileNotFoundError:
            with open('settings.json', 'w') as f:
                f.write(json.dumps({
                    "telegram": {
                        "name": "123",
                        "api_id": 123,
                        "api_hash": "123",
                        "bot_token": "123:123bot",
                        "admins": []
                    },
                    "mysql": {
                        "host": "0.0.0.0",
                        "port": 3306,
                        "user": "root",
                        "password": "passwod",
                        "database": "telegrambot"
                    }
                }, indent=4))

    async def generate_password(self, length: int = 16, special_chars: bool = False) -> str:
        """
        Generate a random password
        :param length:
        :param special_chars:
        :return:
        """
        import secrets
        import string

        alphabet = string.ascii_letters + string.digits
        if special_chars:
            alphabet += string.punctuation
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    async def encrypt_file(self, key: str, memory_file: BytesIO) -> BytesIO:
        """
        Cripta un file
        :param key:
        :param memory_file:
        :return: file_encrypted
        """
        fernet = Fernet(key)
        memory_file.seek(0)
        file_encrypted = fernet.encrypt(memory_file.read())
        memory_file.close()
        return BytesIO(file_encrypted)

    async def decrypt_file(self, key: str, memory_file: BytesIO) -> BytesIO:
        """
        Decripta un file
        :param key:
        :param memory_file:
        :return: file_decrypted
        """
        fernet = Fernet(key)
        memory_file.seek(0)
        file_decrypted = fernet.decrypt(memory_file.read())
        memory_file.close()
        return BytesIO(file_decrypted)
