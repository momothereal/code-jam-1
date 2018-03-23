# coding=utf-8
import logging

import discord
from discord import Colour
from discord.ext.commands import AutoShardedBot, Context, command

log = logging.getLogger(__name__)


# todo: move this to a new file?
class SnakeDef:
    def __init__(self, common_name, species, image_url, family, genus, short_description, wiki_link):
        self.common_name = common_name
        self.species = species
        self.image_url = image_url
        self.family = family
        self.genus = genus
        self.short_description = short_description
        self.wiki_link = wiki_link

    def as_embed(self):
        # returns a discord embed with the snek
        embed = discord.Embed()
        embed.title = self.species + " (" + self.common_name + ")"
        embed.colour = Colour.green()
        embed.url = self.wiki_link
        embed.add_field(name="Family", value=self.family)
        embed.add_field(name="Genus", value=self.genus)
        embed.add_field(name="Species", value=self.species)
        embed.set_thumbnail(url=self.image_url)
        embed.description = self.short_description
        return embed


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

        """
        Go online and fetch information about a snake

        The information includes the name of the snake, a picture of the snake, and various other pieces of info.
        What information you get for the snake is up to you. Be creative!

        If "python" is given as the snake name, you should return information about the programming language, but with
        all the information you'd provide for a real snake. Try to have some fun with this!

        :param name: Optional, the name of the snake to get information for - omit for a random snake
        :return: A dict containing information on a snake
        """

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
    # Any additional commands can be placed here. Be creative, but keep it to a reasonable amount!


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
