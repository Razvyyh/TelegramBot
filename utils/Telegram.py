import contextlib
import json
import pyrogram

from typing import Union
from pyrogram import Client
from pyrogram.enums import ParseMode
from pyrogram.errors import MessageIdInvalid
from pyrogram.types import InlineKeyboardMarkup, CallbackQuery, Message
from utils import Utils
from utils import PoolNotFound, MySQLClient


class TelegramClient(Client):
    def __init__(self, mysql, utils) -> None:
        # LOADS SETTINGS, DATABASE AND SETS VARIABLES
        self.settings: dict = json.loads(open("settings.json", encoding="UTF-8").read())
        self.mysql: MySQLClient = mysql
        self.utils: Utils = utils

        name: str = self.settings.get("telegram", {}).get("name", "123")
        api_id: str = self.settings.get("telegram", {}).get("api_id", 123)
        api_hash: str = self.settings.get("telegram", {}).get("api_hash", "123")
        bot_token: str = self.settings.get("telegram", {}).get("bot_token", "123:123bot")
        self.admins: list = self.settings.get("telegram", {}).get("admins", [])
        self.cache: dict = {}

        self.last_message: dict = {}
        self.waits: dict = {
            "private_key": [],
            "encrypt_file": [],
            "decrypt_file": []
        }

        super().__init__(
            name=name,
            api_id=api_id,
            api_hash=api_hash,
            bot_token=bot_token,
            plugins=dict(root="plugins"),
            parse_mode=ParseMode.HTML,
            workdir="sessions",
            workers=50
        )

    async def callback_edit(self, user_id: int, text: str, buttons: list) -> None:
        """
        Edit last bot message of bot
        :param user_id:
        :param text:
        :param buttons:
        :return:
        """
        with contextlib.suppress(MessageIdInvalid):
            await self.last_message[user_id].edit(
                text=text,
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )

    async def update_last_message(self, update: Union[Message, CallbackQuery]) -> None:
        """
        Update last message of bot
        :param update:
        :return:
        """
        if isinstance(update, CallbackQuery):
            self.last_message[update.from_user.id] = update.message
        else:
            self.last_message[update.from_user.id] = update

    async def wait_input(self, user_id: int, type: str) -> None:
        """
        Wait input
        :param user_id:
        :param type:
        :return:
        """
        if type not in self.waits:
            raise Exception("Invalid type")

        self.waits[type].append(user_id)

    async def get_unique_id(self, user_id: int) -> int:
        """
        Get user by user_id
        :param user_id: User ID
        :return: User
        """
        if not self.mysql.pool:
            raise PoolNotFound("Pool not found")

        return await self.mysql.exec("SELECT id FROM users WHERE user_id = %s", user_id)

    async def start_telegram(self) -> None:
        """
        Start telegram client
        :return:
        """
        try:
            # uvloop.install()
            await self.start()
        except pyrogram.errors.exceptions.bad_request_400.ApiIdInvalid as e:
            raise Exception('Invalid API ID/HASH') from e
