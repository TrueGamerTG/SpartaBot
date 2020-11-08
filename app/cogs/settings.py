import discord
from database import database
from discord.ext import commands


async def set_muterole_perms(guild, role):
    failed = 0
    worked = 0
    for channel in guild.channels:
        try:
            await channel.set_permissions(
                role, send_messages=False,
                add_reactions=False
            )
            worked += 1
        except Exception as e:
            print(e)
            failed += 1
    return worked, failed


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name='muterole',
        invoke_without_command=True
    )
    @commands.has_guild_permissions(
        manage_roles=True, manage_channels=True,
    )
    @commands.guild_only()
    async def set_muterole(
        self, ctx,
        muterole: discord.Role
    ):
        update_guild = \
            """UPDATE guilds
            SET muterole=?
            WHERE id=?"""

        await database.create_guild_data(self.bot, ctx.guild)

        conn = self.bot.db.conn
        async with self.bot.db.lock:
            await conn.execute(
                update_guild, [muterole.id, ctx.guild.id]
            )
            await conn.commit()

        await ctx.send(
            f"Set the muterole to **{muterole.name}**\n"
            "Setting permissions..."
        )

        async with ctx.typing():
            await set_muterole_perms(ctx.guild, muterole)
        await ctx.send("Finished.")


def setup(bot):
    bot.add_cog(Settings(bot))
