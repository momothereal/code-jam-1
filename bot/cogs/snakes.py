# coding=utf-8
import asyncio
import logging
import os
import pickle
import random
from typing import Dict


import discord
from discord.ext.commands import AutoShardedBot, Context, command, group

from pymarkovchain import MarkovChain

import res.snakes.common_snakes
from res.rattle.rattleconfig import RATTLES

import bot.sneks
from bot.sneks.hatching import hatching, hatching_snakes
from bot.sneks.sal import SnakeAndLaddersGame
from bot.sneks.sneks import Embeddable, SnakeDef, scrape_itis, snakify

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

        # libopus
        libopus = os.environ.get('LIBOPUS')
        if libopus is None:
            libopus = "libopus"
        discord.opus.load_opus(libopus)

        # ffmpeg
        self.ffmpeg_executable = os.environ.get('FFMPEG')
        if self.ffmpeg_executable is None:
            self.ffmpeg_executable = 'ffmpeg'

        # snakes and ladders
        self.active_sal: Dict[discord.TextChannel, SnakeAndLaddersGame] = {}

        # check if the snake list pickle-file exists
        pickle_file_path = 'sneks.pickle'
        if not os.path.isfile(pickle_file_path):
            log.warning("No \'sneks.pickle\' file could be found, random snakes are disabled!")
            self.snake_list = []
        else:
            # load pickle
            with open(pickle_file_path, 'rb') as data:
                self.snake_list = pickle.load(data)

    async def get_snek(self, name: str = None) -> Embeddable:
        """
        Gets information about a snek
        :param name: the name of the snek
        :return: snek
        """
        if name is not None and name.lower() == "python":
            # return info about language
            return SNEK_PYTHON

        if name is None:
            # check if the pickle file is there
            if len(self.snake_list) is 0:
                return None
            # random snake
            name = random.choice(self.snake_list).lower()

        if name is not None:
            if name.lower() in res.snakes.common_snakes.REWRITES:
                name = res.snakes.common_snakes.REWRITES[name.lower()]
            return await scrape_itis(name.lower())

    @command(name="snakes.get()", aliases=["snakes.get"])
    async def get(self, ctx: Context, name: str = None):
        """
        Get info about a snek!
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

    @command(name="snakes.draw()", aliases=["snakes.draw"])
    async def draw(self, ctx: Context):
        """
        Draws a random snek using Perlin noise
        """
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(self.send_perlin_snek(ctx), loop)

    @command(name="snakes.rattle()", aliases=["snakes.rattle"])
    async def rattle(self, ctx: Context):
        """
        Play a snake rattle in your voice channel
        """
        author: discord.Member = ctx.author
        if author.voice is None or author.voice.channel is None:
            await ctx.send(author.mention + " You are not in a voice channel!")
            return
        try:
            voice_channel = author.voice.channel
            voice_client: discord.VoiceClient = await voice_channel.connect()
            # select random rattle
            rattle = os.path.join('res', 'rattle', random.choice(RATTLES))
            source = discord.FFmpegPCMAudio(
                rattle,
                executable=self.ffmpeg_executable
            )
            # plays the sound, then dispatches the end_voice event to close the voice client
            voice_client.play(source, after=lambda x: self.bot.dispatch("end_voice", voice_client))

        except discord.ClientException as e:
            log.error(e)
            return

    # event handler for voice client termination
    async def on_end_voice(self, voice_client):
        await voice_client.disconnect()

    @group()
    async def sal(self, ctx: Context):
        """
        Command group for Snakes and Ladders

        - Create a S&L game: sal create
        - Join a S&L game: sal join
        - Leave a S&L game: sal leave
        - Cancel a S&L game (author): sal cancel
        - Start a S&L game (author): sal start
        - Roll the dice: sal roll OR roll
        """
        if ctx.invoked_subcommand is None:
            # alias for 'sal roll' -> roll()
            if ctx.subcommand_passed is not None and ctx.subcommand_passed.lower() == "roll":
                await self.bot.get_command("roll()").invoke(ctx)
                return
            await ctx.send(ctx.author.mention + ": Unknown S&L command.")

    @sal.command(name="create()", aliases=["create"])
    async def create_sal(self, ctx: Context):
        """
        Create a Snakes and Ladders in the channel.
        """
        # check if there is already a game in this channel
        channel: discord.TextChannel = ctx.channel
        if channel in self.active_sal:
            await ctx.send(ctx.author.mention + " A game is already in progress in this channel.")
            return
        game = SnakeAndLaddersGame(snakes=self, channel=channel, author=ctx.author)
        self.active_sal[channel] = game
        await game.open_game()

    @sal.command(name="join()", aliases=["join"])
    async def join_sal(self, ctx: Context):
        """
        Join a Snakes and Ladders game in the channel.
        """
        channel: discord.TextChannel = ctx.channel
        if channel not in self.active_sal:
            await ctx.send(ctx.author.mention + " There is no active Snakes & Ladders game in this channel.")
            return
        game = self.active_sal[channel]
        await game.player_join(ctx.author)

    @sal.command(name="leave()", aliases=["leave", "quit"])
    async def leave_sal(self, ctx: Context):
        """
        Leave the Snakes and Ladders game.
        """
        channel: discord.TextChannel = ctx.channel
        if channel not in self.active_sal:
            await ctx.send(ctx.author.mention + " There is no active Snakes & Ladders game in this channel.")
            return
        game = self.active_sal[channel]
        await game.player_leave(ctx.author)

    @sal.command(name="cancel()", aliases=["cancel"])
    async def cancel_sal(self, ctx: Context):
        """
        Cancel the Snakes and Ladders game (author only).
        """
        channel: discord.TextChannel = ctx.channel
        if channel not in self.active_sal:
            await ctx.send(ctx.author.mention + " There is no active Snakes & Ladders game in this channel.")
            return
        game = self.active_sal[channel]
        await game.cancel_game(ctx.author)

    @sal.command(name="start()", aliases=["start"])
    async def start_sal(self, ctx: Context):
        """
        Start the Snakes and Ladders game (author only).
        """
        channel: discord.TextChannel = ctx.channel
        if channel not in self.active_sal:
            await ctx.send(ctx.author.mention + " There is no active Snakes & Ladders game in this channel.")
            return
        game = self.active_sal[channel]
        await game.start_game(ctx.author)

    @command(name="roll()", aliases=["sal roll", "roll"])
    async def roll_sal(self, ctx: Context):
        """
        Roll the dice in Snakes and Ladders.
        """
        channel: discord.TextChannel = ctx.channel
        if channel not in self.active_sal:
            await ctx.send(ctx.author.mention + " There is no active Snakes & Ladders game in this channel.")
            return
        game = self.active_sal[channel]
        await game.player_roll(ctx.author)

    @command(name="snakes.snakeme()", aliases=["snakes.snakeme", "snakeme"])
    async def snakeme(self, ctx: Context):
        """
        How would I talk if I were a snake?
        :param ctx: context
        :return: you, snakified based on your Discord message history
        """
        mentions = [member for member in ctx.message.mentions if member.id != self.bot.user.id]
        author = ctx.message.author if (len(mentions) == 0) else ctx.message.mentions[0]
        channel: discord.TextChannel = ctx.channel

        channels = [channel for channel in ctx.message.guild.channels if isinstance(channel, discord.TextChannel)]
        log.debug("Pulling messages from channels:{0}".format([c.name for c in channels]))

        channels_messages = [await channel.history(limit=10000).flatten() for channel in channels]
        msgs = [msg for channel_messages in channels_messages for msg in channel_messages]

        my_msgs = [msg for msg in msgs if msg.author.id == author.id][:MSG_MAX]
        log.debug("Received {0} messages ({1} max messages) from user {2}".format(len(my_msgs), MSG_MAX, author.name))
        my_msgs_content = "\n".join([msg.content for msg in my_msgs])

        mc = MarkovChain()
        mc.generateDatabase(my_msgs_content)
        sentence = mc.generateString()

        snakeme = discord.Embed()
        snakeme.set_author(name="{0}#{1}".format(author.name, author.discriminator),
                           icon_url="https://cdn.discordapp.com/avatars/{0}/{1}".format(
                               author.id, author.avatar) if author.avatar is not None else
                           "https://img00.deviantart.net/eee3/i/2017/168/3/4/"
                           "discord__app__avatar_rev1_by_nodeviantarthere-dbd2tp9.png")
        snakeme.description = "*{0}*".format(
            snakify(sentence) if sentence is not None else ":question: Not enough messages")
        await channel.send(embed=snakeme)

    @command(name="snakes.hatch()", aliases=["snakes.hatch", "hatch"])
    async def hatch(self, ctx: Context):
        """
        Hatches your personal snake
        :param ctx: context
        :return: baby snake
        """
        channel: discord.TextChannel = ctx.channel

        my_snake = list(hatching_snakes.keys())[random.randint(0, 3)]
        my_snake_img = hatching_snakes[my_snake]
        log.debug(my_snake_img)

        m = await channel.send(embed=discord.Embed(description="Hatching your snake :snake:..."))
        await asyncio.sleep(1)

        for i in range(len(hatching)):
            hatch_embed = discord.Embed(description=hatching[i])
            await m.edit(embed=hatch_embed)
            await asyncio.sleep(1)
        # await m.edit(embed = discord.Embed().set_thumbnail(url="https://i.imgur.com/5QHH4If.jpg"))
        await asyncio.sleep(1)
        await m.delete()

        my_snake_embed = discord.Embed(description=":tada: Congrats! You hatched: **{0}**".format(my_snake))
        my_snake_embed.set_thumbnail(url=my_snake_img)
        my_snake_embed.set_footer(
            text=" Owner: {0}#{1}".format(ctx.message.author.name, ctx.message.author.discriminator))
        await channel.send(embed=my_snake_embed)

    @asyncio.coroutine
    async def send_perlin_snek(self, ctx):
        factory = bot.sneks.perlin.PerlinNoiseFactory(dimension=1, octaves=2)
        image_frame = bot.sneks.perlinsneks.create_snek_frame(factory)
        png_bytes = bot.sneks.perlinsneks.frame_to_png_bytes(image_frame)

        file = discord.File(png_bytes, filename='snek.png')
        await ctx.send(file=file)


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
