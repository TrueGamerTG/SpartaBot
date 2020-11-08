import discord
from discord.ext import commands


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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


def setup(bot):
    bot.add_cog(Mod(bot))
