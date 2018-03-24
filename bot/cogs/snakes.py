# coding=utf-8
import io
import logging
import math
import random

import discord
from PIL import Image
from PIL.ImageDraw import ImageDraw
from discord.ext.commands import AutoShardedBot, Context, command

import bot.sneks.perlin as perlin
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

    @command(name="snakes.draw()", aliases=["snakes.draw"])
    async def draw(self, ctx: Context):
        stream = self.generate_snake_image()
        file = discord.File(stream, filename='snek.png')
        await ctx.send(file=file)
        pass

    def generate_snake_image(self) -> bytes:
        """
        Generate a CGI snek using perlin noise
        :return: the binary data of the PNG image
        """
        fac = perlin.PerlinNoiseFactory(dimension=1, octaves=2)
        img_size = 200
        margins = 50
        start_x = random.randint(margins, img_size - margins)
        start_y = random.randint(margins, img_size - margins)
        points = [(start_x, start_y)]
        snake_length = 12
        snake_color = 0x15c7ea
        text_color = 0xf2ea15
        background_color = 0x0

        for i in range(0, snake_length):
            angle = math.radians(fac.get_plain_noise((1 / (snake_length + 1)) * (i + 1)) * 360)
            curr_point = points[i]
            segment_length = random.randint(15, 20)
            next_x = curr_point[0] + segment_length * math.cos(angle)
            next_y = curr_point[1] + segment_length * math.sin(angle)
            points.append((next_x, next_y))

        # normalize bounds
        min_dimensions = [start_x, start_y]
        max_dimensions = [start_x, start_y]
        for p in points:
            if p[0] < min_dimensions[0]:
                min_dimensions[0] = p[0]
            if p[0] > max_dimensions[0]:
                max_dimensions[0] = p[0]
            if p[1] < min_dimensions[1]:
                min_dimensions[1] = p[1]
            if p[1] > max_dimensions[1]:
                max_dimensions[1] = p[1]

        # shift towards middle
        dimension_range = (max_dimensions[0] - min_dimensions[0], max_dimensions[1] - min_dimensions[1])
        shift = (
            img_size / 2 - (dimension_range[0] / 2 + min_dimensions[0]),
            img_size / 2 - (dimension_range[1] / 2 + min_dimensions[1])
        )

        img = Image.new(mode='RGB', size=(img_size, img_size), color=background_color)
        draw = ImageDraw(img)
        for i in range(1, len(points)):
            p = points[i]
            prev = points[i - 1]
            draw.line(
                (shift[0] + prev[0], shift[1] + prev[1], shift[0] + p[0], shift[1] + p[1]),
                width=8,
                fill=snake_color
            )
        draw.multiline_text((img_size - margins, img_size - margins), text="snek\nit\nup", fill=text_color)
        del draw
        stream = io.BytesIO()
        img.save(stream, format='PNG')
        return stream.getvalue()


def setup(bot):
    bot.add_cog(Snakes(bot))
    log.info("Cog loaded: Snakes")
