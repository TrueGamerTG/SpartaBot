import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
PREFIX = os.getenv("PREFIX")


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_prefix = PREFIX

    async def close():
        print("Logging Out")


bot = Bot(
    # TODO: Make callable prefix
    command_prefix=PREFIX
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
    try:
        await bot.start(TOKEN)
    finally:
        await bot.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())