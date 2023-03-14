import asyncio
import datetime
import time

import psutil
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from utils import TelegramClient, AntiSpam


@Client.on_callback_query(filters.regex("^server_status$"))
@AntiSpam
async def server_status(self: TelegramClient, query: CallbackQuery):
    # TODO: This is temporary solution, I will change it later
    await query.answer("🖥 | Updating all stats...")

    cpu_usage: str = f"{psutil.cpu_percent()}%"
    ram_usage: str = f"{psutil.virtual_memory().percent}%"
    disk_usage: str = f"{psutil.disk_usage('/').percent}%"
    tasks: int = len(asyncio.all_tasks())
    load_avg: str = f"{psutil.getloadavg()[0]}"
    uptime: str = str(datetime.timedelta(seconds=round(time.time() - psutil.boot_time())))

    text: str = f"<b>🏘 Home » 📊 Server stats</b>\n\n • CPU: {cpu_usage}\n • RAM: {ram_usage}\n • Disk: {disk_usage}\n • Tasks: {tasks}\n • Load average: {load_avg}\n • Uptime: {uptime}\n\n<i>To update the stats you need to click the below button</i>"

    buttons: list = [
        [
            InlineKeyboardButton(text="🔄 Update", callback_data="server_status")
        ],
        [
            InlineKeyboardButton(text="🔙 Back", callback_data="start")
        ]
    ]

    await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)
    await self.update_last_message(update=query)
