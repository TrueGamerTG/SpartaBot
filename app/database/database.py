from asyncio import Lock
import discord
import aiosqlite as asq


async def create_user_data(bot, user: discord.User):
    check_user = """SELECT * FROM users WHERE id=?"""
    create_user = """INSERT INTO users (id) VALUES (?)"""

    conn = bot.db.conn
    async with bot.db.lock:
        cursor = await conn.execute(check_user, [user.id])
        sql_user = await cursor.fetchone()
        if sql_user is None:
            await conn.execute(
                create_user, [user.id]
            )
        await conn.commit()


async def create_guild_data(bot, guild: discord.Guild):
    check_guild = """SELECT * FROM guilds WHERE id=?"""
    create_guild = """INSERT INTO guilds (id) VALUES (?)"""

    conn = bot.db.conn
    async with bot.db.lock:
        cursor = await conn.execute(check_guild, [guild.id])
        sql_guild = await cursor.fetchone()
        if sql_guild is None:
            await conn.execute(create_guild, [guild.id])
        await conn.commit()


class Database:
    def __init__(self, dbpath):
        self.path = dbpath
        self.conn = None
        self.lock = Lock()

    async def open(self):
        conn = await asq.connect(self.path)
        await conn.execute(
            "PRAGMA foreign_keys=True"
        )
        conn.row_factory = self._dict_factory
        self.conn = conn
        await self.create_tables()

    def _dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    async def _create_table(self, sql):
        async with self.lock:
            c = await self.conn.cursor()
            await c.execute(sql)
            await self.conn.commit()

    async def create_tables(self):
        guild_table = \
            """CREATE TABLE IF NOT EXISTS guilds (
                id INTEGER PRIMARY KEY,

                prefix TEXT DEFAULT null,

                welcome_channel INTEGER DEFAULT null,
                leave_channel INTEGER DEFAULT null,
                welcome_msg TEXT DEFAULT null,
                leave_msg TEXT DEFAULT null,

                muterole INTEGER DEFAULT null,

                delete_links bool DEFAULT false
            )"""

        webhooks_table = \
            """CREATE TABLE IF NOT EXISTS webhooks (
                webhook_url TEXT NOT NULL,
                channel_id INTEGER NOT NULL
            )"""

        users_table = \
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY
            )"""

        warn_table = \
            """CREATE TABLE IF NOT EXISTS warns (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,

                reason text NOT NULL,

                FOREIGN KEY (user_id) REFERENCES users (id)
                    ON DELETE CASCADE,
                FOREIGN KEY (guild_id) REFERENCES guilds (id)
                    ON DELETE CASCADE
            )"""

        joinrole_table = \
            """CREATE TABLE IF NOT EXISTS joinroles (
                id INTEGER PRIMARY KEY,
                role_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,

                FOREIGN KEY (guild_id) REFERENCES guilds (id)
                    ON DELETE CASCADE
            )"""

        afk_table = \
            """CREATE TABLE IF NOT EXISTS afks (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                guild_id INTEGER DEFAULT null,

                message TEXT DEFAULT null,

                FOREIGN KEY (guild_id) REFERENCES guilds (id)
                    ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id)
                    ON DELETE CASCADE
            )"""

        reminder_table = \
            """CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,

                message TEXT NOT NULL,
                remind_time TIMESTAMP NOT NULL
            )"""

        await self._create_table(guild_table)
        await self._create_table(webhooks_table)
        await self._create_table(users_table)
        await self._create_table(warn_table)
        await self._create_table(joinrole_table)
        await self._create_table(afk_table)
        await self._create_table(reminder_table)
