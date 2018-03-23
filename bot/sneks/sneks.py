import discord


class SnakeDef:
    """
    Represents a snek
    """

    def __init__(self, common_name = "Not known", species = "Not known", image_url = "", family = "Not known", genus = "Not known", short_description = "No description", wiki_link = "No wikipedia link"):
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
        embed.colour = discord.Colour.green()
        embed.url = self.wiki_link
        embed.add_field(name="Family", value=self.family)
        embed.add_field(name="Genus", value=self.genus)
        embed.add_field(name="Species", value=self.species)
        embed.set_thumbnail(url=self.image_url)
        embed.description = self.short_description
        return embed

