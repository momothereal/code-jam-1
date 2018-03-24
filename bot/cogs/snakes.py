# coding=utf-8
import logging

import discord
from discord.ext.commands import AutoShardedBot, Context, command

from bot.sneks.sneks import Embeddable, SnakeDef, scrape_itis, snakify
from pymarkovchain import MarkovChain

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

# max messages to train on per user 
MSG_MAX = 100

class Snakes:
    """
    Snake-related commands
    """

    def __init__(self, bot: AutoShardedBot):
        self.bot = bot

    async def get_snek(self, name: str = None) -> Embeddable:
        """
        Gets information about a snek
        :param name: the name of the snek
        :return: snek
        """
        if name is not None and name.lower() == "python":
            # return info about language
            return SNEK_PYTHON

        web_search = search.search(name)
        if(web_search is not None):
            return web_search
        # todo: find a random snek online if there name is null
        # todo: scrape the web to find the lost sneks
        if name is not None:
            return await scrape_itis(name)

    @command(name="snakes.get()", aliases=["snakes.get"])
    async def get(self, ctx: Context, name: str = None):
        """
        Get info about a snek!
        :param ctx: context
        :param name: name of snek
        :return: snek
        """
        # fetch data for a snek
        await ctx.send("Fetching data for " + name + "..." if name is not None else "Finding a random snek!")
        data = await self.get_snek(name)
        if data is None:
            await ctx.send("sssorry I can't find that snek :(", embed=SNEK_SAD)
            return
        channel: discord.TextChannel = ctx.channel
        embed = data.as_embed()
        log.debug("Sending embed: " + str(data.__dict__))
        await channel.send(embed=embed)


    @command(name="snakes.snakeme()",aliases=["snakes.snakeme","snakeme"])
    async def snakeme(self, ctx: Context):
        # takes your last messages, trains a simple markov chain generator on what you've said, snakifies your response
        author = ctx.message.author if(len(ctx.message.mentions) == 0) else ctx.message.mentions[0]
        channel : discord.TextChannel = ctx.channel

        channels = [ channel for channel in ctx.message.guild.channels if isinstance(channel,discord.TextChannel) ]
        channels_messages = [ await channel.history(limit=1000).flatten() for channel in channels]
        msgs = [msg for channel_messages in channels_messages for msg in channel_messages][:MSG_MAX]

        my_msgs = list(filter(lambda msg: msg.author == author, msgs))
        my_msgs_content = "\n".join(list(map(lambda x:x.content, my_msgs)))

        mc = MarkovChain()
        mc.generateDatabase(my_msgs_content)
        sentence = mc.generateString()

        snakeme = discord.Embed()
        snakeme.set_author(name="{}#{} Snake".format(author.name,author.discriminator), icon_url = "https://cdn.discordapp.com/avatars/{}/{}".format(author.id,author.avatar))
        snakeme.description = "*{}*".format(snakify(sentence) if sentence is not None else ":question: Not enough messages")
        await channel.send(snakeme)

    @command(name="snakes.hatch()", aliases=["snakes.hatch"])
    async def hatch(self,ctx: Context):
        

def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
