from typing import Union

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from utils import TelegramClient


@Client.on_message(filters.command("start") & filters.private & ~filters.me)
@Client.on_callback_query(filters.regex("start"))
async def start(self: TelegramClient, update: Union[Message, CallbackQuery]):
    text: str = f"<b>🏘 Home</b>\n\nWelcome {update.from_user.mention} on {self.me.mention}!"
    user_id: int = update.from_user.id

    buttons: list = [
        [
            InlineKeyboardButton(text="🛡 Protector", callback_data="protector"),
            InlineKeyboardButton(text="📊 Server stats", callback_data="server_status")
        ],
        [
            InlineKeyboardButton(text="👨‍💻 Developer", url="https://t.me/razvyyh")
        ]
    ]

    if isinstance(update, CallbackQuery):
        await update.message.edit(text=text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)
        await self.update_last_message(update=update)
    else:
        bot_msg: Message = await self.send_message(chat_id=user_id, text=text,
                                                   reply_markup=InlineKeyboardMarkup(buttons),
                                                   disable_web_page_preview=True)
        await self.update_last_message(update=bot_msg)

    await self.mysql.check_user(user_id=user_id)
