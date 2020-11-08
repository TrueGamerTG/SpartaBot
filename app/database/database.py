import aiosqlite as asq
from asyncio import Lock


class Database:
    def __init__(self, dbpath):
        self.path = dbpath
        self.conn = None
        self.lock = Lock()

    async def open(self):
        # Create connection object
        await self.create_tables()

    async def create_tables(self):
        guild_table = \
            """CREATE TABLE IF NOT EXISTS guilds (
                id INTEGER PRIMARY KEY,

                prefix TEXT DEFAULT null,

                welcome_channel INTEGER DEFAULT null,
                leave_channel INTEGER DEFAULT null,
                welcome_msg TEXT DEFAULT null,
                leave_msg TEXT DEFAULT null,

                delete_links bool DEFAULT false,
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
