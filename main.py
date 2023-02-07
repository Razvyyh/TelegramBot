import asyncio
import pyrogram

from utils import TelegramClient, Utils, MySQLClient


class Main:
    def __init__(self):
        self.utils = Utils(version="1.0.0")
        self.utils.initialize()

        self.mysql = MySQLClient()
        self.telegram = TelegramClient(mysql=self.mysql, utils=self.utils)

    async def run(self):
        """
        Run the bot
        """
        await self.mysql.create_pool()
        await self.telegram.start()

        app = await self.telegram.get_me()
        print(f"[+] Bot logged as {app.first_name} ({app.id})")
        print("[+] Bot successfully started")
        # uvloop.install()
        await pyrogram.idle()
        print("[+] Bot successfully stopped")
        await self.telegram.stop()


if __name__ == "__main__":
    """
    Main entry point for the bot
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Main().run())
