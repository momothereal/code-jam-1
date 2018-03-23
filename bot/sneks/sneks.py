import discord
import requests
from bs4 import BeautifulSoup
from wikipedia import wikipedia
import json


class SnakeDef:
    """
    Represents a snek
    """

    def __init__(self, common_name="", species="", image_url="", family="", genus="", short_description="",
                 wiki_link=""):
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
        embed.set_image(url=self.image_url)
        embed.description = self.short_description
        return embed


def find_image_url(name: str) -> str:
    req_url = "https://api.qwant.com/api/search/images?count=1&offset=1&q={}".format(name)
    res = requests.get(url=req_url, headers={"User-Agent": "Mozilla/5.0"})
    j = json.JSONDecoder().decode(res.content.decode("utf-8"))
    image_url = j['data']['result']['items'][0]['media']
    return image_url


def scrape_dbpedia(name: str) -> SnakeDef:
    res = requests.get(url="http://dbpedia.org/page/{}".format(name))
    html = res.content
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table", "description table table-striped")
    rows = table.find_all("tr", {'class': ['even', 'odd']})

    snek = SnakeDef()
    snek.short_description = wikipedia.summary(name)
    snek.wiki_link = "https://en.wikipedia.org/wiki/{}".format(name)
    snek.image_url = find_image_url(name) if not None else ""

    for i in range(1, len(rows)):
        row = rows[i]
        property = row.find("td", "property").find("a")
        val: str = row.find_all("td")[1].find("ul").find("li").find("span").find_all(recursive=False)[0].text
        if ":" in val:
            val = val.split(":")[-1]

        if property['href'].endswith("/family"):
            snek.family = val
        elif property['href'].endswith("/genus") and snek.genus is "":
            snek.genus = val
        elif property['href'].endswith('/binomial'):
            snek.species = val
            snek.common_name = val
        elif property['href'].endswith('/name'):
            snek.species = val
            snek.common_name = val

    return snek
