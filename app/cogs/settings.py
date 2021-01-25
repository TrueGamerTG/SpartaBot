import discord
from discord.ext import commands

from database import database


async def set_muterole_perms(guild, role):
    failed = 0
    worked = 0
    for channel in guild.channels:
        try:
            await channel.set_permissions(
                role, send_messages=False, add_reactions=False
            )
            worked += 1
        except Exception as e:
            print(e)
            failed += 1
    return worked, failed


async def set_muterole(bot, guild, muterole):
    update_guild = """UPDATE guilds
        SET muterole=?
        WHERE id=?"""

    await database.create_guild_data(bot, guild)

    conn = bot.db.conn
    async with bot.db.lock:
        await conn.execute(update_guild, [muterole.id, guild.id])
        await conn.commit()


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="muterole", invoke_without_command=True)
    @commands.has_guild_permissions(manage_roles=True, manage_channels=True)
    @commands.guild_only()
    async def muterole(self, ctx, muterole: discord.Role):
        await set_muterole(self.bot, ctx.guild, muterole)

        await ctx.send(
            f"Set the muterole to **{muterole.name}**\n" "Setting permissions..."
        )

        async with ctx.typing():
            await set_muterole_perms(ctx.guild, muterole)

        await ctx.send("Finished.")

    @muterole.command(name="create")
    @commands.has_guild_permissions(manage_roles=True, manage_channels=True)
    @commands.guild_only()
    async def create_muterole(self, ctx):
        muterole = await ctx.guild.create_role(name="muted")
        await set_muterole(self.bot, ctx.guild, muterole)

        await ctx.send(
            f"Created and set the muterole to **{muterole.name}**\n"
            "Setting permissions..."
        )

        async with ctx.typing():
            await set_muterole_perms(ctx.guild, muterole)

        await ctx.send("Finished")

    @muterole.command(name="update")
    @commands.has_guild_permissions(manage_roles=True, manage_channels=True)
    @commands.guild_only()
    async def update_muterole(self, ctx):
        get_muterole = """SELECT * FROM guilds WHERE id=?"""

        conn = self.bot.db.conn
        async with self.bot.db.lock:
            cursor = await conn.execute(get_muterole, [ctx.guild.id])
            sql_muterole = await cursor.fetchone()

        if sql_muterole is None:
            await ctx.send("You do not have a muterole set.")
            return

        muterole = ctx.guild.get_role(sql_muterole["id"])
        if muterole is None:
            await ctx.send("The muterole was deleted.")
            return

        await ctx.send("Setting permissions...")

        async with ctx.typing():
            await set_muterole_perms(ctx.guild, muterole)

        await ctx.send("Finished")

    @commands.command(name="welcomechannel", aliases=["wc"])
    @commands.has_guild_permissions(manage_roles=True, manage_channels=True)
    @commands.guild_only()
    async def welcome_channel(self, ctx, welcome_channel: discord.TextChannel):
        update_guild = """UPDATE guilds
            SET welcome_channel=?
            WHERE id=?"""

        await database.create_guild_data(self.bot, ctx.guild)

        conn = self.bot.db.conn
        async with self.bot.db.lock:
            await conn.execute(update_guild, [welcome_channel.id, ctx.guild.id])
            await conn.commit()

        await ctx.send(
            f"Your server's welcome channel has been set to {welcome_channel.mention}"
        )


def setup(bot):
    bot.add_cog(Settings(bot))
