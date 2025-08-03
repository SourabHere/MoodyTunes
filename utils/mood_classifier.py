import httpx
import urllib.parse
from dotenv import load_dotenv
import os

load_dotenv()

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")


MOOD_MAP = {
    "dance": ["dance", "club", "edm", "electronic", "house", "party"],
    "happy": ["happy", "upbeat", "fun", "pop", "cheerful", "joy", "sunny"],
    "chill": ["chill", "ambient", "relax", "lofi", "soft", "smooth", "calm"],
    "sad": ["sad", "melancholy", "depressing", "blue", "emo"],
    "car_drive": ["road trip", "car", "driving", "travel", "indie rock", "alternative"]
}


def classify_mood_from_tags(tags: list[str]) -> str:
    tag_set = set(t.lower() for t in tags)
    for mood, keywords in MOOD_MAP.items():
        if any(keyword in tag_set for keyword in keywords):
            return mood
    return "unknown"
    

async def get_lastfm_tags(artist: str, track: str):
    base_url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "track.getInfo",
        "api_key": LASTFM_API_KEY,
        "artist": artist,
        "track": track,
        "format": "json"
    }
    
    
    query = urllib.parse.urlencode(params)
    url = f"{base_url}?{query}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            return []

        data = response.json()
        tags = data.get("track", {}).get("toptags", {}).get("tag", [])
        return [tag["name"] for tag in tags]


async def get_all_lastfm_tags():
    url = f"http://ws.audioscrobbler.com/2.0/?method=tag.getTopTags&api_key={LASTFM_API_KEY}&format=json"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            return []

        data = response.json()
        tags = data.get("toptags", {}).get("tag", [])
        return [tag["name"] for tag in tags]