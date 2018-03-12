# flat_scraper.py - Scrapes bezrealitky.cz for 3+1 flat in Prague

import requests
import os
import bs4
import logging
import re
import math     # just to get math.ceil (?) - better way?
logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
# url for Prague, 3+1 flat
# TODO: Add praha-{place} from command line(?) for more narrow search into the url and custom disposition
#
disposition = "disposition%5B0%5D=2-1"     # if 2 dispositions: disposition%5B0%5D=2-1&disposition%5B1%5D=3-1 - B0 -> B1; 3 is B0 B1 B2 etc.
place = "praha"

url = "https://www.bezrealitky.cz/vypis/nabidka-pronajem/byt/{0}?{1}&order=time_order_desc".format(place, disposition)

logging.debug("Downloading url: {}".format(url))
# Download the web page
res = requests.get(url)
res.raise_for_status()

# Initialize bs4
soup = bs4.BeautifulSoup(res.text, "lxml")

# Get the number of results
numberOfResults = soup.select(".counter")[0].getText()
# TODO: Number of results: compare it with the saved value (aka value from before).
# regex for the number in the number of results
resultsRegex = re.compile("\d+")
numberOfResults = resultsRegex.search(numberOfResults)
logging.debug("Show numberOfResults: {}".format(numberOfResults.group()))



# wrap it all in while statement until page != the max page.

# calculate the number of pages, since it is 10 results per page
numberOfPages = math.ceil(int(numberOfResults.group()) / 10)

names = []
prices = []
links = []
# Regex to match against the text in the result on the web page
nameRegex = re.compile("""((\w+\s)?\w+,)\s       # match the first part of the offer: "(word )? word " 
                       Praha                  # match the word Praha
                       \s-\s                  # match the " - "
                       (\w+(\s\w+)?)""",         # match the rest of the offer "word ( word)?"
                       re.VERBOSE)
page = 1
while page != numberOfPages + 1:

    logging.debug("Getting details of flats on page {}".format(page))

    # Select the links to results on current page
    flats = soup.select(".details h2.header a")

    # Done: Get the name of the offer: Place and price
    # Select p element that has the price in it
    priceElem = soup.select(".details p.price")

    # Select p element that has short-url in it
    shortUrlElem = soup.select(".details p.short-url")

    # iterate over Tag objects in flats and prices list
    for index, value in enumerate(flats):

        name = flats[index].getText()
        price = priceElem[index].getText()
        link = shortUrlElem[index].getText()


        name = nameRegex.search(name).group()
        # name = "{}: {}".format(name, price)
        names.append(name)
        prices.append(price)
        links.append(link)

    # Get another page url
    url = "https://www.bezrealitky.cz/vypis/nabidka-pronajem/byt/{0}?{1}&order=time_order_desc&page={2}".format(place, disposition, (page + 1))
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, "lxml")
    page += 1
offers = list(zip(names, prices, links))
logging.debug("Number of scraped offers: {}".format(len(offers)))
logging.debug("Zipped: {}".format(offers))

# Log all the offers into a file
# open up the same file 2 times - once for reading, once for appending the new offer

with open("offer{}.txt".format(disposition[len(disposition)-3:len(disposition)]), "a") as file_write, open("offer{}.txt".format(disposition[len(disposition)-3:len(disposition)]),"r") as file_read:
    lines = file_read.readlines()
    print(lines)
    for offer in offers:
        # join the tuple elements together
        joinedOffer = " ".join(offer)
        # add newline character to the end
        if (joinedOffer+"\n") not in lines:
            logging.info("Writing to the file")
            file_write.write(joinedOffer)
            file_write.write("\n")

# TODO: When new offer added or removed, send email with the offer (maybe?) Or all of them again?





