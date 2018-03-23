import urllib
from bs4 import BeautifulSoup as BS

from .sneks import SnakeDef

DBPEDIA_BASE_URL = "http://dbpedia.org/page/"
WIKI_BASE_URL = "http://wikipedia.org/wiki/page/"

def fc(s):
	return s[0].upper() + s[1:] if (s is not None and len(s) > 0) else None 

def query_url(query):
	return DBPEDIA_BASE_URL + fc("_".join(query.split(" ")))


def add_oc(ocs,oc_raw):
	if oc_raw["rel"][0] in ocs:
		ocs[oc_raw["rel"][0]].append(oc_raw.getText())
	else:
		ocs[oc_raw["rel"][0]] = [oc_raw.getText()]


def db_strip(s):
	return s.replace("dbo:","").replace("dbr:","")


def search(query):

	snake = SnakeDef()
	# already assume query is not None, not checking 
	snake_query_url = query_url(query)
	

	try:
		html = urllib.request.urlopen(snake_query_url).read()
	except urllib.error.HTTPError:
		return None

	soup = BS(html, "lxml")

	oc_raws = soup.findAll("a",{ "class": "uri", "rel": True})
	ocs = {}
	for oc_raw in oc_raws:
		add_oc(ocs,oc_raw)


	# result has a valid dbpedia page but not a snake
	if("dbr:Snake" not in ocs["dbo:order"]):
		return None

	# reformat, messily written

	snake.family = ",".join(list(map(db_strip,ocs["dbo:family"])))
	snake.genus = ",".join(list(map(db_strip,ocs["dbo:genus"])))
	snake.species = " ".join(list(map(fc, query.split(" "))))
	snake.wiki_link = WIKI_BASE_URL + fc("_".join(query.split(" ")))

	return snake











