import asyncio
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from pretty_help import Navigation, PrettyHelp

from database import database

load_dotenv()

TOKEN = os.getenv("SPARTA_TOKEN")
PREFIX = "sb!"  # TODO: Make this s! when rewrite is finished
INTENTS = discord.Intents(messages=True, guilds=True, members=True)
THEME = discord.Color.blurple()

help_nav = Navigation()


class Bot(commands.Bot):
    def __init__(self, db, *args, **kwargs):
        self.db = db
        super().__init__(*args, **kwargs)
        self.default_prefix = PREFIX

    async def close(self):
        print("Logging Out")


db = database.Database("app/database/db.sqlite3")
bot = Bot(
    # TODO: Make callable prefix
    db,
    command_prefix=PREFIX,
    help_command=PrettyHelp(navigation=help_nav, color=THEME),
)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} in {len(bot.guilds)} guilds!")


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)


async def run():
    bot.load_extension("cogs.mod")
    bot.load_extension("cogs.settings")
    bot.load_extension("cogs.fun")
    bot.load_extension("cogs.topgg")
    try:
        await db.open()
        await bot.start(TOKEN)
    finally:
        await bot.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
