import json

import aiomysql
import pymysql

from aiomysql import Pool


class PoolNotFound(Exception):
    """ Raise error when pool is not started yet or not initializated"""
    pass


class MySQLClient:
    def __init__(self):
        self.settings: dict = json.loads(open("settings.json", encoding="UTF-8").read())

        self.host: str = self.settings.get("mysql", {}).get("host", "0.0.0.0")
        self.port: int = self.settings.get("mysql", {}).get("port", 3306)
        self.user: str = self.settings.get("mysql", {}).get("user", "root")
        self.password: str = self.settings.get("mysql", {}).get("password", "password")
        self.db: str = self.settings.get("mysql", {}).get("database", "telegrambot")
        self.pool = None

    async def create_pool(self):
        """ Create pool - Should be run on startup"""
        try:
            self.pool: Pool = await aiomysql.create_pool(
                maxsize=20,
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db=self.db,
                autocommit=True
            )
            await self.start()
            print("[+] MySQL pool successfully created")
        except KeyboardInterrupt as e:
            raise KeyboardInterrupt() from e

    async def start(self):
        """ Run on startup """

        tables: list = [table[0] for table in await self.exec("SHOW TABLES")]

        if 'users' not in tables:
            await self.exec(
                """CREATE TABLE IF NOT EXISTS users(
                    id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
                    user_id BIGINT NOT NULL,
                    private_key VARCHAR(255) DEFAULT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)
            print("[+] Table 'users' successfully created")

    async def check_user(self, user_id: int):
        """
        Check if user exists in database and create if not exists
        :param user_id: User ID
        :return: True if user exists, False if not
        """
        if not self.pool:
            raise PoolNotFound("Pool not found")

        check: bool = await self.exec("SELECT * FROM users WHERE user_id = %s", user_id)
        if not check:
            await self.exec("INSERT INTO users(user_id) VALUES(%s)", user_id)

        return check

    async def get_private_key(self, user_id: int):
        """
        Get user private key
        :param user_id: User ID
        :return: Private key
        """
        if not self.pool:
            raise PoolNotFound("Pool not found")

        key: list = await self.exec("SELECT private_key FROM users WHERE user_id = %s", user_id)

        try:
            return key[0][0]
        except IndexError:
            return None

    async def set_private_key(self, user_id: int, private_key: str):
        """
        Set user private key
        :param user_id:
        :param private_key:
        :return:
        """

        if not self.pool:
            raise PoolNotFound("Pool not found")

        await self.exec("UPDATE users SET private_key = %s WHERE user_id = %s", (private_key, user_id))

    async def exec(self, query: str, values=None):
        """ Execute queries """

        if not self.pool:
            raise PoolNotFound("Pool not found")

        async with self.pool.acquire() as conn:
            conn: aiomysql.Connection
            async with conn.cursor() as c:
                try:
                    c: aiomysql.Cursor
                    await c.execute(query, values)
                    if 'select' in query.lower() or 'show' in query.lower():
                        return await c.fetchall()
                    else:
                        await conn.commit()
                except pymysql.err.ProgrammingError as e:
                    print(e, query)
