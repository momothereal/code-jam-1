# coding=utf-8
import logging

import discord
from discord.ext.commands import AutoShardedBot, Context, command

from bot.sneks.sneks import SnakeDef, snakify

from pymarkovchain import MarkovChain

import bot.sneks.search as search

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

# max messages per user
MSG_MAX = 100

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

        web_search = search.search(name)
        if(web_search is not None):
            return web_search
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

    @command()
    # takes your last messages, trains an simple markov chain generator on what you've said, and snakifies it
    async def snakeme(self, ctx: Context):

        channel : discord.TextChannel = ctx.channel
        msgs = await channel.history(limit=1000).flatten()

        my_msgs = list(filter(lambda msg: msg.author == ctx.message.author, msgs))
        await channel.send("Retrieved " + str(len(my_msgs)) + " messages from me.")

        my_msgs_content = list(map(lambda x:x.content, my_msgs))
        print(my_msgs_content)

        mc = MarkovChain()
        mc.generateDatabase("\n".join(my_msgs_content))
        sentence = mc.generateString()
        await channel.send(snakify(sentence) if sentence is not None else "Not enough messages.")



def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
