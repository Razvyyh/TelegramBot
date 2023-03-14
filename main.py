import asyncio
import logging

import coloredlogs
import pyrogram

from utils import TelegramClient, Utils, MySQLClient


class Main:
    def __init__(self):
        self.log = logging.getLogger('bot')
        self.utils: Utils = Utils(version="1.0.0")
        self.utils.initialize()

        coloredlogs.install(fmt="[%(asctime)s] %(message)s", datefmt="%I:%M:%S", logger=self.log)

        self.mysql: MySQLClient = MySQLClient(logs=self.log)
        self.telegram: TelegramClient = TelegramClient(logs=self.log, mysql=self.mysql, utils=self.utils)

    async def run(self):
        """
        Run the bot
        """
        await self.mysql.create_pool()
        await self.telegram.start()

        app = await self.telegram.get_me()
        self.log.info(f"[+] Bot logged as {app.first_name} ({app.id})")
        self.log.info("[+] Bot successfully started")
        # uvloop.install()
        await pyrogram.idle()
        self.log.info("[+] Bot successfully stopped")
        await self.telegram.stop()


if __name__ == "__main__":
    """
    Main entry point for the bot
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Main().run())
