from typing import Union
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from utils import TelegramClient


@Client.on_message(filters.command("start") & filters.private & ~filters.me)
@Client.on_callback_query(filters.regex("start"))
async def start(self: TelegramClient, message: Union[Message, CallbackQuery]):

    text: str = f"<b>🏘 Home</b>\n\nWelcome {message.from_user.mention} on {self.me.mention}!"
    user_id: int = message.from_user.id

    buttons: list = [
        [
            InlineKeyboardButton("🛡 Protector", callback_data="protector")
        ],
        [
            InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/razvyyh")
        ]
    ]

    if isinstance(message, CallbackQuery):
        await message.message.edit(text=text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)
        await self.update_last_message(message)
    else:
        bot_msg: Message = await self.send_message(chat_id=message.chat.id, text=text,
                                                   reply_markup=InlineKeyboardMarkup(buttons),
                                                   disable_web_page_preview=True)
        await self.update_last_message(bot_msg)

    await self.mysql.check_user(user_id)
