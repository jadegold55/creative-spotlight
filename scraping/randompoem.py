import random
import bs4 as BeautifulSoup
import requests
import logging

from datetime import datetime

links = []


# the point of this file might be more for having an event everyday which
# the bot posts the new poem of the day from poetry foundation, but for now this is just a test to make sure i can scrape the page and get the poem links. I will need to add some error handling and logging to make sure it runs smoothly, especially if i want to run it on a schedule.
def scrape(author=None, title=None):
    random_linect = random.randint(4, 20)
    if author:
        url = "https://poetrydb.org/author,linecount/" + author + ";" + random_linect
    elif title:
        url = "https://poetrydb.org/title/" + title
    else:
        url = "https://poetrydb.org/linecount/15"
    try:
        response = requests.get(url)
        response.raise_for_status()
        poems = response.json()
        # will raise an error if the response is not successful, which we can catch and log
        # while poem is empty or too long fetch one until we get a good one
        # too many requests?
        if isinstance(poems, list) and len(poems) > 0:
            poem = random.choice(poems)
            return {
                "title": poem.get("title", "Unknown Title"),
                "author": poem.get("author", "Unknown Author"),
                "content": "\n".join(poem.get("lines", [])),
            }

        else:
            print("API returned an error or empty result:", poems)
            return None  # don't want to return empty poem

    except Exception as e:
        print(f"Error fetching from Poetrydb: {e}")
        return None  # only happnes with badrequest, but want to return empty list so bot can handle it gracefully and not try to create an embed with empty data.


if __name__ == "__main__":

    scraped_poems = scrape()
    print(scraped_poems)
