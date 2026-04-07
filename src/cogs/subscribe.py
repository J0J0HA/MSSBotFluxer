import asyncio
from enum import Enum, auto
import fluxer
from fluxer import Cog, has_role
import logging

logger = logging.getLogger(__name__)


class Success(Enum):
    SUBBED = auto()
    ALREADY_SUBBED = auto()
    FAILED_TO_SUB = auto()
    UNSUBBED = auto()
    ALREADY_UNSUBBED = auto()
    FAILED_TO_UNSUB = auto()


class Roles(Cog):
    def __init__(self, bot: fluxer.Bot):
        super().__init__(bot)

    async def _get_role_for_guild(self, guild_id: int):
        roles = await (await self.bot.fetch_guild(guild_id)).fetch_roles()
        for role in roles:
            if role.name == "News":
                return role
        return None

    async def _subscribe(self, member: fluxer.GuildMember) -> Success:
        """Subscribes a member to @News"""
        role = await self._get_role_for_guild(member.guild_id)
        if not role:
            return Success.FAILED_TO_SUB
        if member.has_role(role.id):
            return Success.ALREADY_SUBBED
        try:
            await member.add_role(role.id)
        except fluxer.errors.Forbidden:
            return Success.FAILED_TO_SUB
        return Success.SUBBED

    async def _unsubscribe(self, member: fluxer.GuildMember):
        """Unsubscribes a member from @News"""
        role = await self._get_role_for_guild(member.guild_id)
        if not role:
            return Success.FAILED_TO_UNSUB
        if not member.has_role(role.id):
            return Success.ALREADY_UNSUBBED
        try:
            await member.remove_role(role.id)
        except fluxer.errors.Forbidden:
            return Success.FAILED_TO_UNSUB
        return Success.UNSUBBED

    async def _handle_success_for_ctx(self, ctx: fluxer.Message, result: Success):
        if result == Success.ALREADY_SUBBED:
            reply = await ctx.reply("Already subscribed to \@News.")
        elif result == Success.SUBBED:
            reply = await ctx.reply("Subscribed to \@News.")
        elif result == Success.FAILED_TO_SUB:
            reply = await ctx.reply("Failed to subscribe to \@News.")
        elif result == Success.ALREADY_UNSUBBED:
            reply = await ctx.reply("Already unsubscribed from \@News.")
        elif result == Success.UNSUBBED:
            reply = await ctx.reply("Unsubscribed from \@News.")
        elif result == Success.FAILED_TO_UNSUB:
            reply = await ctx.reply("Failed to unsubscribe from \@News.")
        await asyncio.sleep(5)
        await ctx.delete()
        await reply.delete()

    @Cog.listener()
    async def on_member_join(self, ctx: dict):
        guild = await self.bot.fetch_guild(ctx.get("guild_id"))
        member = await guild.fetch_member(ctx.get("user").get("id"))
        result = await self._subscribe(member)
        if result != Success.SUBBED:
            logging.error(f"Failed to subscribe {ctx.get('user').get('username')} to \@News on join.")

    @Cog.command()
    async def sub(self, ctx: fluxer.Message):
        logger.info(f"Received sub command from {ctx.author.display_name}")
        author_member = await ctx.guild.fetch_member(ctx.author.id)
        result = await self._subscribe(author_member)
        await self._handle_success_for_ctx(ctx, result)

    @Cog.command()
    async def unsub(self, ctx: fluxer.Message):
        """Unsubscribes from @News"""
        logger.info(f"Received unsub command from {ctx.author.display_name}")
        author_member = await ctx.guild.fetch_member(ctx.author.id)
        result = await self._unsubscribe(author_member)
        await self._handle_success_for_ctx(ctx, result)

    @Cog.command()
    @has_role(name="Admin")
    async def forcesub(self, ctx: fluxer.Message):
        """Subscribes someone else to @News"""
        logger.info(f"Received forcesub command from {ctx.author.display_name}")

        if len(ctx.mentions) != 1:
            await ctx.reply("Please mention exactly one user.")
            await asyncio.sleep(5)
            await ctx.delete()
            return

        member = await ctx.guild.fetch_member(ctx.mentions[0].id)
        result = await self._subscribe(member)
        await self._handle_success_for_ctx(ctx, result)

    @Cog.command()
    @has_role(name="Admin")
    async def forceunsub(self, ctx: fluxer.Message):
        """Unsubscribes someone else from @News"""
        logger.info(f"Received forceunsub command from {ctx.author.display_name}")

        if len(ctx.mentions) != 1:
            await ctx.reply("Please mention exactly one user.")
            await asyncio.sleep(5)
            await ctx.delete()
            return

        member = await ctx.guild.fetch_member(ctx.mentions[0].id)
        result = await self._unsubscribe(member)
        await self._handle_success_for_ctx(ctx, result)


async def setup(bot: fluxer.Bot):
    await bot.add_cog(Roles(bot))
