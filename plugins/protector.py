import asyncio

from cryptography.fernet import Fernet, InvalidToken
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from utils import TelegramClient


@Client.on_callback_query(filters.regex("^protector$"))
async def protector(self: TelegramClient, query: CallbackQuery):
    text: str = f"<b>🏘 Home » 🛡 Protector</b>\n\nYou can use this menu to protect your files with an ecryption key"
    user_id: int = query.from_user.id

    buttons: list = [
        [
            InlineKeyboardButton("🔐 Encrypt", callback_data="protector.encrypt"),
            InlineKeyboardButton("🔓 Decrypt", callback_data="protector.decrypt")
        ],
        [
            InlineKeyboardButton("🔑 My key", callback_data="protector.my_key")
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data="start")
        ]
    ]

    await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)
    await self.update_last_message(query)

    if user_id in self.waits["encrypt_file"]: self.waits["encrypt_file"].remove(user_id)
    if user_id in self.waits["decrypt_file"]: self.waits["decrypt_file"].remove(user_id)
    if user_id in self.waits["private_key"]: self.waits["private_key"].remove(user_id)


@Client.on_callback_query(filters.regex("^protector."))
async def protector_data(self: TelegramClient, query: CallbackQuery):
    _, category = query.data.split(".")
    user_id: int = query.from_user.id

    private_key: str = await self.mysql.get_private_key(user_id)

    if category == "encrypt" and private_key is not None:
        text: str = f"<b>🏘 Home » 🛡 Protector » 🔐 Encrypt</b>\n\nSend me the file you want to encrypt"
        buttons: list = [
            [
                InlineKeyboardButton("🔙 Back", callback_data="protector")
            ]
        ]
        self.waits["encrypt_file"].append(user_id)

    elif category == "decrypt" and private_key is not None:
        text: str = f"<b>🏘 Home » 🛡 Protector » 🔓 Decrypt</b>\n\nSend me the file you want to decrypt"
        buttons: list = [
            [
                InlineKeyboardButton("🔙 Back", callback_data="protector")
            ]
        ]
        self.waits["decrypt_file"].append(user_id)

    elif category == "my_key":
        key: str = f"<spoiler>{private_key}</spoiler>" if private_key is not None else "Not set"
        text: str = f"<b>🏘 Home » 🛡 Protector » 🔑 My key</b>\n\n • Private key: {key}\n\nGenerate a key or use your own key!"
        buttons: list = [
            [
                InlineKeyboardButton("🔄 Generate", callback_data="protector.generate"),
                InlineKeyboardButton("🔑 Use my key", callback_data="protector.use_my_key")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="protector")
            ]
        ]

    elif category == "generate":
        await query.answer("🔄 | Generating a new key...")
        key = Fernet.generate_key().decode()
        await self.mysql.set_private_key(user_id, key)

        query.data = "protector.my_key"
        return await protector_data(self, query)

    elif category == "use_my_key":
        text: str = f"<b>🏘 Home » 🛡 Protector » 🔑 My key</b>\n\nSend me your private key"
        buttons: list = [
            [
                InlineKeyboardButton("🔙 Back", callback_data="protector.my_key")
            ]
        ]
        self.waits["private_key"].append(user_id)

    else:
        return await query.answer("❗️ | You must first set your private key!", show_alert=True)

    await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)
    await self.update_last_message(query)


@Client.on_message(filters.private, group=10)
async def wait_private_key(self: TelegramClient, message: Message):
    user_id: int = message.from_user.id

    if user_id in self.waits["private_key"]:
        await message.delete()

        buttons: list = [
            [
                InlineKeyboardButton("🔄 Generate", callback_data="protector.generate"),
                InlineKeyboardButton("🔑 Use my key", callback_data="protector.use_my_key")
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data="protector")
            ]
        ]

        self.waits["private_key"].remove(user_id)

        key: str = message.text
        await self.mysql.set_private_key(user_id, key)

        await self.callback_edit(
            user_id=user_id,
            text=f"<b>🏘 Home » 🛡 Protector » 🔑 My key</b>\n\n • Key: <spoiler>{key}</spoiler>\n\nYou have successfully set the private key!",
            buttons=buttons
        )
        return await self.update_last_message(message)

    elif user_id in self.waits["encrypt_file"]:
        await message.delete()

        private_key: str = await self.mysql.get_private_key(user_id)

        try:
            memory_file = await self.download_media(message=message, in_memory=True)
        except ValueError:
            return await self.callback_edit(
                user_id=user_id,
                text="<b>🏘 Home » 🛡 Protector » 🔐 Encrypt</b>\n\n❗️ | The file is too large or invalid!",
                buttons=[
                    [
                        InlineKeyboardButton("🔙 Back", callback_data="protector")
                    ]
                ]
            )

        encrypted_file = await self.utils.encrypt_file(key=private_key, memory_file=memory_file)

        await self.send_document(chat_id=user_id, document=encrypted_file, file_name=message.document.file_name,
                                 caption="🔐 | Encrypted file")

        return self.waits["encrypt_file"].remove(user_id)

    elif user_id in self.waits["decrypt_file"]:
        await message.delete()

        private_key: str = await self.mysql.get_private_key(user_id)

        try:
            memory_file = await self.download_media(message, in_memory=True)
            decrypted_file = await self.utils.decrypt_file(key=private_key, memory_file=memory_file)
        except InvalidToken:
            return await self.callback_edit(
                user_id=user_id,
                text="<b>🏘 Home » 🛡 Protector » ❗️ Decrypt</b>\n\nThe file you sent has not been encrypted by this bot!",
                buttons=[
                    [
                        InlineKeyboardButton("🔄 Retry", callback_data="protector.decrypt")
                    ]
                ]
            )
        except ValueError:
            return await self.callback_edit(
                user_id=user_id,
                text="<b>🏘 Home » 🛡 Protector » ❗️ Decrypt</b>\n\n❗️ | The file is too large or invalid!",
                buttons=[
                    [
                        InlineKeyboardButton("🔙 Back", callback_data="protector")
                    ]
                ]
            )

        await self.send_document(chat_id=user_id, document=decrypted_file, file_name=message.document.file_name,
                                 caption="🔓 | Decrypted file")

        return self.waits["decrypt_file"].remove(user_id)
