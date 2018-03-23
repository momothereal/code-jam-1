import json
import re

import discord
import requests
from bs4 import BeautifulSoup
from wikipedia import wikipedia

# the search URL for the ITIS database
ITIS_BASE_URL = "https://itis.gov/servlet/SingleRpt/{}"
ITIS_SEARCH_URL = ITIS_BASE_URL.format("SingleRpt")


class Embeddable:
    def as_embed(self) -> discord.Embed:
        pass


class SnakeDef(Embeddable):
    """
    Represents a snek species
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
        if len(embed.description) > 1000:
            embed.description = embed.description[:997] + "..."
        return embed


class SnakeGroup(Embeddable):

    def __init__(self, common_name="None", scientific_name="None", image_url="", rank="Unknown", sub=[],
                 short_description="A snake group", link=""):
        self.link = link
        self.common_name = common_name
        self.scientific_name = scientific_name
        self.image_url = image_url
        self.rank = rank
        self.sub = sub
        self.short_description = short_description

    def as_embed(self):
        embed = discord.Embed()
        embed.title = self.scientific_name + ((" (" + self.common_name + ")") if self.common_name is not None else "")
        embed.description = self.short_description
        if len(embed.description) > 1000:
            embed.description = embed.description[:997] + "..."
        embed.colour = discord.Colour.green()
        embed.url = self.link
        embed.set_image(url=self.image_url)
        if self.common_name is not "None":
            embed.add_field(name="Common Name", value=self.common_name)
        embed.add_field(name="Taxonomic Rank", value=self.rank)
        return embed


def find_image_url(name: str) -> str:
    req_url = "https://api.qwant.com/api/search/images?count=1&offset=1&q={}+snake".format(name.replace(" ", "+"))
    res = requests.get(url=req_url, headers={"User-Agent": "Mozilla/5.0"})
    if res.status_code != 200:
        return ""
    j = json.JSONDecoder().decode(res.content.decode("utf-8"))
    image_url = j['data']['result']['items'][0]['media']
    return image_url


def is_itis_table_empty(soup) -> bool:
    return "No Records Found." in str(soup)


def itis_find_link(soup) -> str:
    return ITIS_BASE_URL.format(soup.find("a")['href'])


def scrape_itis_page(url: str) -> Embeddable:
    res = requests.get(url=url)
    html = res.content.decode('iso-8859-1')
    # check taxonomic rank first
    soup = BeautifulSoup(html, "html.parser")
    rank = soup.find("td", text="Taxonomic Rank:").parent.find("td", {"class": "datafield"}).get_text(strip=True,
                                                                                                      separator=' ')
    common_names = soup.find("td", text="Common Name(s):").parent.find("td", {"class": "datafield"}).get_text(
        strip=True, separator=' ')
    if "[" in common_names:
        common_names = common_names.split('[')[0].strip(" ")
    scientific_name = ' '.join(
        soup.find("td", text=re.compile("(\\s+)" + rank)).parent.find("td", {"class": "datafield"})
            .get_text(strip=True, separator=' ')
            .split(",")[0].replace(u'\xa0', ' ').split(' ')[0:2])
    print(rank)

    if rank == "Species" or rank == "Subspecies":
        embeddable = SnakeDef()
        embeddable.common_name = common_names if common_names != "" else "None"
        embeddable.species = scientific_name
        try:
            embeddable.short_description = wikipedia.summary(scientific_name)
        except wikipedia.PageError:
            pass
        embeddable.wiki_link = url
        embeddable.image_url = find_image_url(scientific_name)
        embeddable.genus = \
            soup.find("td", text=re.compile("(\\s+)Genus")).parent.find("td", {"class": "datafield"}).get_text(
                strip=True,
                separator=' ').split(
                ",")[0]
        embeddable.family = \
            soup.find("td", text=re.compile("(\\s+)Family")).parent.find("td", {"class": "datafield"}).get_text(
                strip=True,
                separator=' ').split(
                ",")[0]
    else:
        # its a snek group
        embeddable = SnakeGroup()
        try:
            embeddable.short_description = wikipedia.summary(scientific_name)
        except wikipedia.PageError:
            try:
                embeddable.short_description = wikipedia.summary(common_names)
            except wikipedia.PageError:
                pass
            pass
        embeddable.common_name = common_names
        embeddable.scientific_name = scientific_name
        embeddable.link = url
        embeddable.image_url = find_image_url(scientific_name)
        embeddable.rank = rank

    return embeddable


def scrape_itis(name: str) -> Embeddable:
    form_data = {
        'categories': 'All',
        'Go': 'Search',
        'search_credRating': 'All',
        'search_kingdom': 'Animal',
        'search_span': 'exactly_for',
        'search_topic': 'all',
        'search_value': name,
        'source': 'html'
    }
    print(name.replace(" ", "+"))
    res = requests.post(url=ITIS_SEARCH_URL, data=form_data)
    html = res.content.decode('iso-8859-1')
    if "No Records Found?" in html:
        # abort, no snek
        return None
    soup = BeautifulSoup(html, "html.parser")
    # print(soup)

    tables = soup.find_all("table", {"width": "100%"})
    # print(tables)
    table_common_name = tables[1]
    table_scientific = tables[2]

    is_common_name = not is_itis_table_empty(table_common_name)
    is_scientific = not is_itis_table_empty(table_scientific)

    if not is_common_name and not is_scientific:
        # unknown snek, abort
        return None

    url = None
    if is_scientific:
        url = itis_find_link(table_scientific)
    elif is_common_name:
        url = itis_find_link(table_common_name)
    if url is None:
        return

    # follow link!
    print(url)

    return scrape_itis_page(url)


def scrape_dbpedia(name: str) -> SnakeDef:
    res = requests.get(url="http://dbpedia.org/page/{}".format(name.replace(" ", "_")))
    html = res.content
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find("table", "description table table-striped")
    rows = table.find_all("tr", {'class': ['even', 'odd']})

    snek = SnakeDef()
    snek.short_description = wikipedia.summary(name)
    snek.wiki_link = "https://en.wikipedia.org/wiki/{}".format(name.replace(" ", "_"))
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
