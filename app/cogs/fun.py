import discord
from discord.ext import commands

from database import database


class Fun(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(
        name="impersonate", aliases=["as"], brief="Impersonate another user"
    )
    @commands.guild_only()
    async def impersonate_user(
        self, ctx: commands.Context, user: discord.Member, *, message: str
    ) -> None:
        get_webhook = """SELECT * FROM webhooks
            WHERE channel_id=$1::integer"""
        delete_webhook = """DELETE FROM webhooks
            WHERE channel_id=$1::integer"""
        create_webhook = """INSERT INTO webhooks (channel_id, webhook_url)
            VALUES ($1::integer, $2::text)"""

        webhook = None
        await ctx.message.delete()

        await database.create_guild_data(self.bot, ctx.guild)
        conn = self.bot.db.conn
        async with self.bot.db.lock:
            cursor = await conn.execute(get_webhook, [ctx.channel.id])
            sql_webhook = await cursor.fetchone()

        if sql_webhook:
            webhook = discord.utils.get(
                await ctx.channel.webhooks(), url=sql_webhook["webhook_url"]
            )
            if not webhook:
                sql_webhook = None
                async with self.bot.db.lock:
                    await conn.execute(delete_webhook, [ctx.channel.id])
                    await conn.commit()

        if sql_webhook is None:
            webhook: discord.Webhook = await ctx.channel.create_webhook(
                name="Sparta impersonate Command",
                reason="Impersonation Command",
            )
            async with self.bot.db.lock:
                await conn.execute(
                    create_webhook, [ctx.channel.id, webhook.url]
                )
                await conn.commit()

        await webhook.send(
            message, username=user.name, avatar_url=user.avatar_url
        )


def setup(bot) -> None:
    bot.add_cog(Fun(bot))
