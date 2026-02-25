import random
import requests
import logging

from datetime import datetime


def scrapeArt():
    url = f"https://api.artic.edu/api/v1/artworks?query[term][is_public_domain]=true&fields=id,title,artist_display,date_display,image_id&limit=1&page={random.randint(1, 1000)}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        artwork = data["data"][0]
        print(f"image id: {artwork.get('image_id')}")
        return {
            "title": artwork.get("title", "Unknown Title"),
            "artist": artwork.get("artist_display", "Unknown Artist"),
            "date": artwork.get("date_display", "Unknown Date"),
            "image_url": (
                f"https://www.artic.edu/iiif/2/{artwork['image_id']}/full/843,/0/default.jpg"
                if artwork.get("image_id")
                else None
            ),
        }
    except Exception as e:
        print(f"Error fetching artwork: {e}")
        return None
