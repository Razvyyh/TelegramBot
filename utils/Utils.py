import asyncio
import json
import os
import zipfile

from io import BytesIO

import aiofiles as aiofiles
from cryptography.fernet import Fernet


class Utils:
    def __init__(self, version: str):
        self.version: str = version

    @staticmethod
    def initialize() -> None:
        """
        Check if settings.json exists if it does not exist it
        creates it create settings.json file.
        :return:
        """
        if not os.path.exists('sessions'):
            os.makedirs('sessions')

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

    @staticmethod
    async def save_settings(settings: dict) -> None:
        """
        Save settings.json
        :param settings:
        :return:
        """
        async with aiofiles.open('settings.json', 'w') as f:
            await f.write(json.dumps(settings, indent=4))

    @staticmethod
    async def generate_password(length: int = 16, special_chars: bool = False) -> str:
        """
        Generate a random password
        :param length:
        :param special_chars:
        :return:
        """
        import secrets
        import string

        alphabet: str = string.ascii_letters + string.digits
        if special_chars:
            alphabet += string.punctuation
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    async def encrypt_file(key: str, memory_file: BytesIO) -> BytesIO:
        """
        Cripta un file
        :param key:
        :param memory_file:
        :return: file_encrypted
        """
        fernet: Fernet = Fernet(key)
        memory_file.seek(0)
        file_encrypted: bytes = fernet.encrypt(memory_file.read())
        memory_file.close()
        return BytesIO(file_encrypted)

    @staticmethod
    async def decrypt_file(key: str, memory_file: BytesIO) -> BytesIO:
        """
        Decripta un file
        :param key:
        :param memory_file:
        :return: file_decrypted
        """
        fernet: Fernet = Fernet(key)
        memory_file.seek(0)
        file_decrypted: bytes = fernet.decrypt(memory_file.read())
        memory_file.close()
        return BytesIO(file_decrypted)

    @staticmethod
    async def zip_folder(folder_path: str, zip_path: str = "archive.zip") -> None:
        loop = asyncio.get_event_loop()

        with zipfile.ZipFile(zip_path, "w") as my_zip:
            for folder_name, sub_folders, filenames in os.walk(folder_path):
                for filename in filenames:
                    file_path = os.path.join(folder_name, filename)
                    await loop.run_in_executor(None, my_zip.write, file_path)
