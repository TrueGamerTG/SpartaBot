import discord
from typing import Union
from discord.ext import commands


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='mute', aliases=['m']
    )
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_guild_permissions(manage_roles=True)
    @commands.guild_only()
    async def mute_user(
        self, ctx,
        user: discord.Member,
        *, reason: str = None
    ):
        get_muterole = """SELECT * FROM guilds WHERE id=?"""
        conn = self.bot.db.conn
        async with self.bot.db.lock:
            cursor = await conn.execute(get_muterole, [ctx.guild.id])
            guild = await cursor.fetchone()

        if guild is None or guild['muterole'] is None:
            await ctx.send(
                "Before you can mute, you must set a muterole. "
                "Please run `muterole <role>`"
            )
            return
        muterole = ctx.guild.get_role(guild['muterole'])
        if muterole is None:
            await ctx.send(
                "The muterole was deleted. Please create a new one."
            )
            return
        await user.add_roles(muterole)
        await ctx.send(f"Muted **{user}**")

    @commands.command(
        name='unmute', aliases=['um']
    )
    @commands.bot_has_permissions(manage_roles=True)
    @commands.has_guild_permissions(manage_roles=True)
    @commands.guild_only()
    async def unmute_user(
        self, ctx,
        user: discord.Member,
        *, reason: str = None
    ):
        get_muterole = """SELECT * FROM guilds WHERE id=?"""
        conn = self.bot.db.conn
        async with self.bot.db.lock:
            cursor = await conn.execute(get_muterole, [ctx.guild.id])
            guild = await cursor.fetchone()

        if guild is None or guild['muterole'] is None:
            await ctx.send(
                "There is no muterole set. Please run `muterole <role>`"
            )
            return

        muterole = ctx.guild.get_role(guild['muterole'])

        if muterole is None:
            await ctx.send(
                "The muterole was deleted. Please create a new one."
            )
            return

        await user.remove_roles(muterole)
        await ctx.send(f"Unmuted **{user}**")

    @commands.command(
        name='clear', aliases=['purge']
    )
    @commands.bot_has_permissions(
        manage_messages=True,
        read_message_history=True
    )
    @commands.has_permissions(manage_messages=True)
    @commands.guild_only()
    async def purge(
        self, ctx,
        limit: int,
        user: discord.User = None
    ):
        def check(message):
            if user is not None and message.author.id != user.id:
                return False
            return True

        await ctx.message.delete()
        purged = await ctx.channel.purge(limit=limit, check=check)

        purge_dict = {}
        for m in purged:
            purge_dict.setdefault(m.author, 0)
            purge_dict[m.author] += 1

        message = f"Cleared {len(purged)} messages:"
        for user, num in purge_dict.items():
            message += f"\n** - {user}:** {num}"

        await ctx.send(message, delete_after=10)

    @commands.command(name="ban")
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, user: Union[discord.Member, int], *, reason=None):
        if not isinstance(user, int):
            if ctx.author.top_role.position <= user.top_role.position \
                    and ctx.guild.owner_id != ctx.author.id:
                await ctx.send(
                    "You cannot ban this user because their role "
                    "is higher than or equal to yours."
                )
                return
        if isinstance(user, int):
            user_str = f"<@{user}>"
            user = discord.Object(id=user)
        else:
            user_str = user
        try:
            await user.send(
                f"You have been **banned** from **{ctx.guild}** server "
                f"due to the following reason:\n**{reason}**"
            )
        except Exception:
            pass
        await ctx.guild.ban(user, reason=reason)
        if reason:
            await ctx.send(
                f"User **{user_str}** has been banned for reason: "
                f"**{reason}**."
            )
        else:
            await ctx.send(f"User **{user_str}** has been banned.")

    @commands.command(name="unban")
    @commands.has_guild_permissions(ban_members=True)
    @commands.guild_only()
    async def unban(
        self, ctx, user: Union[discord.User, int, str],
        *, reason=None
    ):
        if isinstance(user, int):
            user_str = f"<@{user}>"
            user = discord.Object(id=user)
        else:
            user_str = user

        if isinstance(user, str):
            guild_bans = await ctx.guild.bans()
            print(guild_bans)
            try:
                name, tag = user.split('#')
                print(f"<{name}>")
                print(f"<{tag}>")
            except Exception:
                await ctx.send(
                    "Please format the username like this: "
                    "Username#0000"
                )
                return

            banned_user = None
            for gb in guild_bans:
                if gb.user.name == name:
                    if gb.user.discriminator == tag:
                        banned_user = gb

            if banned_user is None:
                await ctx.send("I could not find that user in the bans.")
                return
            await ctx.guild.unban(banned_user.user)
            try:
                await banned_user.send(
                    f"You have been unbanned with reason: {reason}"
                )
            except Exception:
                pass

        else:
            await ctx.guild.unban(user)
            try:
                await user.send(
                    f"You have been unbanned with reason: {reason}"
                )
            except Exception:
                pass

        await ctx.send(f"Unbanned **{user_str}**")

    @commands.command(name="kick")
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.Member = None, *, reason=None):
        if reason is None:
            reason = "No reason provided."

        if ctx.author.top_role.position <= user.top_role.position \
                and ctx.guild.owner_id != ctx.author.id:
            await ctx.send(
                "You cannot kick this user because their role is "
                "higher than or equal to yours."
            )
        else:
            await ctx.guild.kick(user, reason=reason)
            try:
                await user.send(
                    f"You have been **kicked** from **{ctx.guild}** "
                    f"server due to the following reason:\n**{reason}**"
                )
            except Exception:
                pass
            if reason:
                await ctx.send(
                    f"User **{user}** has been kicked "
                    "for reason: **{reason}**."
                )
            else:
                await ctx.send(f"User **{user}** has been kicked.")


def setup(bot):
    bot.add_cog(Mod(bot))
