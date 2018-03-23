# coding=utf-8
import logging

import discord
from discord.ext.commands import AutoShardedBot, Context, command

from bot.sneks.sneks import SnakeDef

log = logging.getLogger(__name__)

# the python snek
SNEK_PYTHON = SnakeDef(
    common_name="Python",
    species="Pseudo lingua",
    image_url="https://momoperes.ca/files/pythonpls.png",
    family="sneks-that-byte",
    genus="\"Programming Language\"",
    short_description="python is a language that you learn because tensorflow has an API for it",
    wiki_link="https://en.wikipedia.org/wiki/Pseudocode"
)

# consolation snek :(
SNEK_SAD = discord.Embed()
SNEK_SAD.title = "sad snek :("
SNEK_SAD.set_image(url="https://momoperes.ca/files/sadsnek.jpeg")


class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    async def get_snek(self, name: str = None) -> SnakeDef:
        if name is not None and name.lower() == "python":
            # return info about language
            return SNEK_PYTHON

        # todo: find a random snek online if there name is null
        # todo: scrape the web to find the lost sneks

    @command()
    async def get(self, ctx: Context, name: str = None):
        # fetch data for a snek
        await ctx.send("Fetching data for " + name + "..." if name is not None else "Finding a random snek!")
        data = await self.get_snek(name)
        if data is None:
            await ctx.send("sssorry I can't find that snek :(", embed=SNEK_SAD)
            return
        channel: discord.TextChannel = ctx.channel
        await channel.send(embed=data.as_embed())


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
