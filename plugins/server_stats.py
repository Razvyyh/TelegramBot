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
    await query.answer("๐ฅ | Updating all stats...")

    cpu_usage: str = f"{psutil.cpu_percent()}%"
    ram_usage: str = f"{psutil.virtual_memory().percent}%"
    disk_usage: str = f"{psutil.disk_usage('/').percent}%"
    tasks: int = len(asyncio.all_tasks())
    load_avg: str = f"{psutil.getloadavg()[0]}"
    uptime: str = str(datetime.timedelta(seconds=round(time.time() - psutil.boot_time())))

    text: str = f"<b>๐ Home ยป ๐ Server stats</b>\n\n โข CPU: {cpu_usage}\n โข RAM: {ram_usage}\n โข Disk: {disk_usage}\n โข Tasks: {tasks}\n โข Load average: {load_avg}\n โข Uptime: {uptime}\n\n<i>To update the stats you need to click the below button</i>"

    buttons: list = [
        [
            InlineKeyboardButton(text="๐ Update", callback_data="server_status")
        ],
        [
            InlineKeyboardButton(text="๐ Back", callback_data="start")
        ]
    ]

    await query.message.edit(text=text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)
    await self.update_last_message(update=query)
