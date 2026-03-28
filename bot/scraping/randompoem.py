import random
import requests
import logging

log = logging.getLogger(__name__)


def scrape(author=None, title=None):
    random_linect = random.randint(4, 20)
    if author:
        url = (
            "https://poetrydb.org/author,linecount/" + author + ";" + str(random_linect)
        )
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
            log.warning("API returned an error or empty result: %s", poems)
            return None

    except Exception as e:
        log.error("Error fetching from Poetrydb: %s", e)
        return None


if __name__ == "__main__":

    scraped_poems = scrape()
    print(scraped_poems)
