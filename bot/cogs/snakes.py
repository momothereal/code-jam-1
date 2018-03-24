# coding=utf-8
import logging
import os
import random

import discord
from discord.ext.commands import AutoShardedBot, Context, command

from bot.sneks.sneks import Embeddable, SnakeDef, scrape_itis

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
        discord.opus.load_opus("libopus")
        self.bot = bot
        self.rattles = [
            'rattle1.mp3',
            'rattle2.mp3',
            'rattle3.mp3',
            'rattle4.mp3'
        ]
        self.ffmpeg_executable = os.environ.get('FFMPEG')

    async def get_snek(self, name: str = None) -> Embeddable:
        """
        Gets information about a snek
        :param name: the name of the snek
        :return: snek
        """
        if name is not None and name.lower() == "python":
            # return info about language
            return SNEK_PYTHON

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

    @command(name="snakes.rattle()", aliases=["snakes.rattle"])
    async def rattle(self, ctx: Context):
        """
        Play a snake rattle in your voice channel
        :param ctx: context
        :return: nothing
        """
        author: discord.Member = ctx.author
        if author.voice is None or author.voice.channel is None:
            await ctx.send(author.mention + " You are not in a voice channel!")
            return
        try:
            voice_channel = author.voice.channel
            voice_client: discord.VoiceClient = await voice_channel.connect()
            # select random rattle
            rattle = os.path.join(os.path.dirname(__file__), '..', '..', 'res', 'rattle', random.choice(self.rattles))
            source = discord.FFmpegPCMAudio(
                rattle,
                executable=self.ffmpeg_executable if not None else 'ffmpeg'
            )
            # plays the sound, then dispatches the end_voice event to close the voice client
            voice_client.play(source, after=lambda x: self.bot.dispatch("end_voice", voice_client))

        except discord.ClientException as e:
            log.error(e)
            return
        pass

    # event handler for voice client termination
    async def on_end_voice(self, voice_client):
        await voice_client.disconnect()


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
