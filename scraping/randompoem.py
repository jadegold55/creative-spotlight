
import bs4 as BeautifulSoup
import requests
import logging

from datetime import datetime
links = []
# the point of this file might be more for having an event everyday which
#the bot posts the new poem of the day from poetry foundation, but for now this is just a test to make sure i can scrape the page and get the poem links. I will need to add some error handling and logging to make sure it runs smoothly, especially if i want to run it on a schedule.
def scrape():
    url = "https://poetrydb.org/random"
    try:
        response = requests.get(url)
        
        poems = response.json()
        if isinstance(poems, list) and len(poems) > 0:
            for poem in poems:
                if len("\n".join(poem.get('lines', []))) < 4096:  # Discord embed description limit
                    return {
                        "title": poem.get('title', 'Unknown Title'),
                        "author": poem.get('author', 'Unknown Author'),
                        "content": "\n".join(poem.get('lines', []))
            }
        else:
            print("API returned an error or empty result:", poem)
            return None
       
    except Exception as e:
        print(f"Error fetching from Poetrydb: {e.with_traceback(e.__traceback__)}")
        return []




if __name__ == "__main__":
    
    scraped_poems = scrape()
    