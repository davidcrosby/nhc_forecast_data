#!/Users/dc/code/hurricanes/bin/python
from bs4 import BeautifulSoup as bs
import requests
import os

def get_soup(url):
    req = requests.get(url)
    return bs(req.content, features = "html.parser")

def get_storm_urls(archive_soup):
    """
    input: beautiful soup object for NHC archive page at some year
    output: dictionary with a list for pacific/atlantic storm hrefs
    """
    atlantic = archive_soup.find("td", {"headers": "al"})
    pacific = archive_soup.find("td", {"headers": "ep"})
    item_to_url = lambda x : x["href"]
    return {
        "atlantic": list(map(item_to_url, atlantic.find_all("a"))),
        "pacific": list(map(item_to_url, pacific.find_all("a")))
    }

def get_preformatted_text(url):
    """
    return the first instance of preformatted text
    """
    body = requests.get(url)
    soup = bs(body.content, features="html.parser")
    return soup.find("pre").text

def parse_preformatted_text_for_forecast(text):
    """
    return text filtered with only positional forecast data
    """
    def is_forecast_line(line):
        line = line.split(" ")
        if len(line) < 2: return False
        first_word, second_word = line[0:2]
        if first_word in ("FORECAST", "OUTLOOK") and second_word == "VALID":
            return True
        return False
    return list(filter(is_forecast_line, text.split("\n")))

def get_forecast_advisories_for(url, out_path):
    """
    Create a file containing the pre-formatted text for each storm advisory
    """
    soup = get_soup(url)
    if soup:
        forecast_tds = soup.find_all("td", {"headers" : "col1"})
        for td in forecast_tds:
            a_tags = list(td.find_all("a"))
            for el in a_tags:
                href = el["href"]
                filename = el.text + ".txt"
                text = get_preformatted_text("https://www.nhc.noaa.gov"+href)
                #text = parse_preformatted_text_for_forecast(text)
                with open(out_path + "/" + filename, "w+") as f:
                    #for line in text: f.write(line)
                    f.write(text)


def create_oceanic_folder(path, basin, advisory_hrefs, url):
    path = path + basin
    for href in advisory_hrefs[basin]:
        name = href.split(".")[0]
        this_path = path + "/" + name
        if not os.path.exists(this_path):
            os.makedirs(this_path) 
        get_forecast_advisories_for(url + href, this_path)


def create_storm_folder(year):
    path = "data/" + year + "/"
    url = "https://www.nhc.noaa.gov/archive/" + year + "/"
    if not os.path.exists(path):
        os.makedirs(path)
    soup = get_soup(url)
    advisory_hrefs = get_storm_urls(soup)
    create_oceanic_folder(path, "pacific", advisory_hrefs, url)
    create_oceanic_folder(path, "atlantic", advisory_hrefs, url)

if __name__ == "__main__":
    create_storm_folder(str(2018))
