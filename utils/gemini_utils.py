import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Dict
import json

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=GEMINI_API_KEY)

# model = genai.GenerativeModel("models/gemini-1.5-pro")
model = genai.GenerativeModel("models/gemini-1.5-flash")
# model = genai.GenerativeModel("models/gemini-2.0-flash-lite")

def classify_songs_by_mood(playlist_name: str, mood: str, songs: List[Dict[str, str]]) -> str:
    """
    Classifies the given list of songs based on the mood using Gemini.

    Args:
        playlist_name: Name of the playlist.
        mood: Mood to filter songs by.
        songs: List of song dicts, each containing 'artist', 'track', 'spotify_url', and 'spotify_id'.

    Returns:
        A JSON string with a filtered list of songs.
    """
    prompt = f'''
    I have the following list of songs from a Spotify playlist named "{playlist_name}".

    The user wants a playlist with a "{mood}" mood.

    Here is the list of songs:
    {songs}

    Please return a filtered list of songs that match the mood "{mood}" in this format only:
    [
      {{"artist": "...", "track": "...", "spotify_id": "...", "mood_match": true}}
    ]

    Respond with only JSON. Avoid extra comments.
    '''

    try:
        print(f"Sending request to Gemini model with prompt: {prompt}")
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return str({"error": str(e)})
    

def classify_song_ids_by_mood(playlist_name: str, mood: str, songs: List[Dict[str, str]]) -> List[Dict[str, str]]:

    prompt = f'''
        You are a music assistant.

        The user wants to create a playlist named "{playlist_name}" with a "{mood}" mood.

        Here is the list of songs:
        {songs}

        Please return a JSON list ONLY in the following format:
        [
        {{"spotify_id": "<id>", "mood_match": true/false}},
        ...
        ]

        Only return valid JSON. No markdown, no explanations, no extra text.
        '''

    try:
        print("Sending Gemini prompt...")
        response = model.generate_content(prompt)
        output = response.text.strip()


        if output.startswith("```json"):
            output = output.replace("```json", "").replace("```", "").strip()

        return json.loads(output)

    except Exception as e:
        return [{"error": str(e)}]


def hello_model() -> str:
    """
    A simple test function to check if the model is working.
    """
    try:
        response = model.generate_content("Say hello")
        return response.text.strip()
    except Exception as e:
        return str({"error": str(e)})