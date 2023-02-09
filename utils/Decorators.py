import asyncio
import contextlib

from datetime import datetime
from functools import wraps
from typing import Callable
from typing import Union
from cachetools import TTLCache
from pyrate_limiter import (BucketFullException, Duration, Limiter,
                            MemoryListBucket, RequestRate)

from pyrogram import Client
from pyrogram.types import CallbackQuery, Message

users: TTLCache = TTLCache(maxsize=128, ttl=60)
blacklist: dict = {}
warns: dict = {}
seconds_to_blacklist: int = 10


class RateLimiter:
    """
    RateLimiter class to limit user's from spamming commands or pressing buttons multiple times
    using leaky bucket algorithm and pyrate_limiter.
    """

    def __init__(self) -> None:
        # 1 requests per seconds
        self.second_rate: RequestRate = RequestRate(2, Duration.SECOND)

        self.limiter: Limiter = Limiter(
            self.second_rate,
            bucket_class=MemoryListBucket,
        )

    async def acquire(self, userid: Union[int, str]) -> bool:
        """
        Acquire a token from the rate limiter.
        :param userid:
        :return:
        """
        with contextlib.suppress(BucketFullException):
            self.limiter.try_acquire(userid)
            return False

        return True


ratelimiter: RateLimiter = RateLimiter()


def AntiSpam(func: Callable) -> Callable:
    """
    Decorator to limit user's from spamming commands or pressing buttons multiple times
    :param func:
    :return:
    """

    @wraps(func)
    async def decorator(client: Client, update: Union[Message, CallbackQuery]):
        user_id: int = update.from_user.id
        is_limited: bool = await ratelimiter.acquire(user_id)

        if user_id in blacklist:
            if (datetime.now() - blacklist[user_id]).seconds >= seconds_to_blacklist:
                blacklist.pop(user_id)
                warns.pop(user_id)
            else:
                return

        if is_limited:
            if user_id not in users:
                if isinstance(update, Message):
                    msg: Message = await update.reply_text(
                        "⚠️ | Please slow down with your actions. Consider how your actions might be difficult to process if sent continuously. Thank you for your cooperation.")
                    await asyncio.sleep(3)
                    await msg.delete()
                    users[user_id]: int = 1
                    return

                elif isinstance(update, CallbackQuery):
                    users[user_id]: int = 1
                    return await update.answer("Heyy relax, breathe. Don't perform too many actions at once!",
                                               show_alert=True)

            elif user_id in users:

                if user_id not in warns:
                    warns.update({user_id: 1})
                    return await update.answer(
                        f"⚠️ | Warn ({warns[user_id]})\n\nPlease take a moment to breathe and slow down with your actions. Consider how your actions might be difficult to process if sent continuously. Thank you for your cooperation.",
                        show_alert=True)
                else:
                    warns[user_id] += 1
                    if warns[user_id] >= 3:
                        blacklist.update({user_id: datetime.now()})
                        return await update.answer(
                            f"❗️| Blacklist\n\nTo keep the bot safe and fast I had to blacklist you for {seconds_to_blacklist} seconds",
                            show_alert=True)
                    else:
                        return await update.answer(
                            f"⚠️ | Warn ({warns[user_id]})\n\nPlease take a moment to breathe and slow down with your actions. Consider how your actions might be difficult to process if sent continuously. Thank you for your cooperation.",
                            show_alert=True)
        return await func(client, update)

    return decorator
