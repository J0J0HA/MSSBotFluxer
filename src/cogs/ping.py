import fluxer
from fluxer import Cog
import logging

logger = logging.getLogger(__name__)


class Ping(Cog):
    def __init__(self, bot: fluxer.Bot):
        super().__init__(bot)

    @Cog.command()
    async def ping(self, ctx: fluxer.Message):
        """Replies with Pong!"""
        logger.info(f"Received ping command from {ctx.author.display_name}")
        await ctx.reply("Pong!")


async def setup(bot: fluxer.Bot):
    await bot.add_cog(Ping(bot))